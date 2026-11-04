"""Unit tests for the human-approval gate (core/approvals.py) and its use in tools."""

import time
from unittest.mock import Mock, patch

import pytest

from core.approvals import (
    ApprovalError,
    ApprovalStatus,
    gate_action,
    get_approval_queue,
)


@pytest.fixture
def queue():
    return get_approval_queue()


class TestGateAction:
    def test_side_effect_action_is_queued_not_executed(self, queue):
        execute = Mock(return_value="done")
        result = gate_action("Some Tool", "email.send_message", {"to": "a@b.c"},
                             read_only=False, execute=execute)
        execute.assert_not_called()
        assert result.startswith("PENDING_HUMAN_APPROVAL")
        pending = queue.list(status=ApprovalStatus.PENDING)
        assert len(pending) == 1
        assert pending[0].action == "email.send_message"
        assert pending[0].id in result

    def test_read_only_action_runs_immediately(self, queue):
        execute = Mock(return_value="rows")
        assert gate_action("T", "calendar.read_events", {}, read_only=True,
                           execute=execute) == "rows"
        execute.assert_called_once()
        assert queue.list() == []

    def test_gate_can_be_disabled_explicitly(self, queue, monkeypatch):
        monkeypatch.setenv("REQUIRE_HUMAN_APPROVAL", "false")
        execute = Mock(return_value="done")
        assert gate_action("T", "email.send_message", {}, read_only=False,
                           execute=execute) == "done"

    def test_gate_on_when_env_unset(self, queue, monkeypatch):
        monkeypatch.delenv("REQUIRE_HUMAN_APPROVAL", raising=False)
        execute = Mock()
        gate_action("T", "email.send_message", {}, read_only=False, execute=execute)
        execute.assert_not_called()


class TestApprovalQueue:
    def _submit(self, queue, execute=None):
        gate_action("T", "filesystem.write_file", {"path": "/x"}, read_only=False,
                    execute=execute or Mock(return_value="written"))
        return queue.list(status=ApprovalStatus.PENDING)[0]

    def test_approve_executes_once_and_records_approver(self, queue):
        execute = Mock(return_value="written")
        action = self._submit(queue, execute)
        decided = queue.approve(action.id, approver="key-abc")
        execute.assert_called_once()
        assert decided.status == ApprovalStatus.EXECUTED
        assert decided.decided_by == "key-abc"
        assert decided.result == "written"

    def test_cannot_approve_twice(self, queue):
        execute = Mock(return_value="ok")
        action = self._submit(queue, execute)
        queue.approve(action.id, approver="a")
        with pytest.raises(ApprovalError):
            queue.approve(action.id, approver="a")
        assert execute.call_count == 1

    def test_reject_never_executes(self, queue):
        execute = Mock()
        action = self._submit(queue, execute)
        decided = queue.reject(action.id, approver="a", reason="no")
        assert decided.status == ApprovalStatus.REJECTED
        with pytest.raises(ApprovalError):
            queue.approve(action.id, approver="a")
        execute.assert_not_called()

    def test_expired_action_cannot_be_approved(self, queue, monkeypatch):
        monkeypatch.setenv("APPROVAL_TTL_SECONDS", "1")
        execute = Mock()
        action = self._submit(queue, execute)
        with patch("core.approvals.time.time", return_value=time.time() + 5):
            with pytest.raises(ApprovalError):
                queue.approve(action.id, approver="a")
        execute.assert_not_called()

    def test_execution_failure_is_recorded(self, queue):
        action = self._submit(queue, Mock(side_effect=RuntimeError("boom")))
        decided = queue.approve(action.id, approver="a")
        assert decided.status == ApprovalStatus.FAILED
        assert "boom" in decided.result

    def test_unknown_id(self, queue):
        with pytest.raises(KeyError):
            queue.approve("nope", approver="a")

    def test_approval_events_are_audited(self, queue):
        with patch("core.approvals.get_audit_logger") as gal:
            action = self._submit(queue)
            queue.approve(action.id, approver="a")
        events = [c.args[0].event_type for c in gal.return_value.log.call_args_list]
        assert "approval.requested" in events
        assert "approval.approved" in events
        assert "approval.executed" in events


class TestToolTransportsAreGated:
    """Side-effecting MCP / n8n calls must not reach the network without approval."""

    @patch("requests.post")
    def test_mcp_write_file_is_queued(self, mock_post, queue):
        from core.tools import WriteFileMCPTool
        result = WriteFileMCPTool()._run(path="/tmp/x", content="hi")
        mock_post.assert_not_called()
        assert result.startswith("PENDING_HUMAN_APPROVAL")

    @patch("requests.post")
    def test_mcp_email_send_is_queued(self, mock_post, queue):
        from core.tools import MCPGmailSendTool
        tool = MCPGmailSendTool()
        tool._run(**{p: "x" for p in _required_params(tool._run)})
        mock_post.assert_not_called()
        assert len(queue.list(status=ApprovalStatus.PENDING)) == 1

    @patch("requests.post")
    def test_mcp_read_file_runs_without_approval(self, mock_post, queue):
        from core.tools import ReadFileMCPTool
        mock_post.return_value = Mock(text="contents", raise_for_status=Mock())
        ReadFileMCPTool()._run(path="/tmp/x")
        mock_post.assert_called_once()
        assert queue.list() == []

    @patch("requests.post")
    def test_n8n_trigger_is_queued_then_runs_after_approval(self, mock_post, queue):
        from core.tools import N8NTriggerWorkflowTool
        mock_post.return_value = Mock(text='data: {"result": "ok"}', raise_for_status=Mock())
        result = N8NTriggerWorkflowTool()._run(workflow_id="wf-1", input_data={"k": 1})
        assert result.startswith("PENDING_HUMAN_APPROVAL")
        mock_post.assert_not_called()

        action = queue.list(status=ApprovalStatus.PENDING)[0]
        queue.approve(action.id, approver="human")
        mock_post.assert_called_once()
        assert mock_post.call_args.kwargs["json"]["params"]["name"] == "execute_workflow"

    @patch("requests.post")
    def test_n8n_search_runs_without_approval(self, mock_post, queue):
        from core.tools import N8NListWorkflowsTool
        mock_post.return_value = Mock(text='data: {"result": []}', raise_for_status=Mock())
        N8NListWorkflowsTool()._run(query="sales")
        mock_post.assert_called_once()

    @pytest.mark.parametrize("cls_name", ["EmailSendingApiTool", "CrmApiTool",
                                          "SequenceAutomationTool"])
    def test_direct_side_effect_tools_are_queued(self, cls_name, queue):
        import core.tools as tools
        tool = getattr(tools, cls_name)()
        args = {p: ({} if p in ("data", "triggers") else [] if p == "steps" else "x")
                for p in _required_params(tool._run)}
        assert tool._run(**args).startswith("PENDING_HUMAN_APPROVAL")


def _required_params(fn):
    import inspect
    return [n for n, p in inspect.signature(fn).parameters.items()
            if p.default is inspect.Parameter.empty
            and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)]
