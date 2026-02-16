"""
Core tools for the agentic system.
These tools can be used by agents to perform various tasks.
"""

import os
import uuid
import json
import logging
import requests
from typing import List, Dict, Any, Optional, ClassVar, Union, Callable

# Configure logging
logger = logging.getLogger(__name__)

# Check if CrewAI is available, if so use its BaseTool, otherwise create a simple base class
try:
    from crewai.tools import BaseTool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    class BaseTool:
        """Simple base class for tools when CrewAI is not available"""
        name: str = "Base Tool"
        description: str = "Base tool class"
        
        def _run(self, *args, **kwargs):
            raise NotImplementedError("Tool not implemented")
        
        def run(self, *args, **kwargs):
            return self._run(*args, **kwargs)

# Import the privateGPT client (legacy)
try:
    from core.privategpt_client import get_privategpt_client
except ImportError:
    get_privategpt_client = None

# ChromaDB for direct RAG access
try:
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

class KnowledgeBaseTool(BaseTool):
    """Direct RAG tool for querying the knowledge base using ChromaDB"""
    
    name: str = "Knowledge Base Query Tool"
    description: str = (
        "Queries the knowledge base for specific information using direct vector search. "
        "Use this to find department-specific information, policies, procedures, best practices, etc. "
        "Input should be a clear, specific question."
    )
    vectorstore_path: str = "vectorstore"
    collection_name: str = "knowledge_base"
    department_filter: Optional[str] = None
    
    def __init__(self, department_filter: Optional[str] = None, vectorstore_path: str = "vectorstore"):
        """Initialize the tool with optional department filter"""
        super().__init__()
        self.department_filter = department_filter
        self.vectorstore_path = vectorstore_path
        self._use_mock = os.environ.get('USE_MOCK_KB', 'false').lower() == 'true'
    
    def _run(self, query: str) -> str:
        """Run the query against the direct RAG vector store"""
        
        # Check if we're in mock mode
        if self._use_mock:
            dept_info = f" for {self.department_filter}" if self.department_filter else ""
            return f"MOCK KB RESPONSE: Found information about '{query}'{dept_info} in the knowledge base. Here's what I know...\n\nThis is simulated knowledge base response for demonstration purposes."
        
        # Check if ChromaDB is available
        if not CHROMADB_AVAILABLE:
            return "Error: ChromaDB not available. Please install chromadb package or use mock mode."
        
        try:
            # Initialize ChromaDB client
            client = chromadb.PersistentClient(path=self.vectorstore_path)
            
            # Get the collection
            collection = client.get_collection(
                name=self.collection_name,
                embedding_function=SentenceTransformerEmbeddingFunction(
                    model_name="nomic-ai/nomic-embed-text-v1.5",
                    trust_remote_code=True
                )
            )
            
            # Prepare the query with department filter if specified
            where_filter = {}
            if self.department_filter:
                where_filter["department"] = self.department_filter
            
            # Query the collection
            results = collection.query(
                query_texts=[query],
                n_results=5,
                where=where_filter if where_filter else None
            )
            
            if not results['documents'] or not results['documents'][0]:
                dept_info = f" in {self.department_filter} department" if self.department_filter else ""
                return f"No relevant information found{dept_info} for your query: '{query}'"
            
            # Format the response
            response_parts = []
            documents = results['documents'][0]
            metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(documents)
            
            for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
                source = metadata.get('source', 'Unknown source')
                dept = metadata.get('department', 'Unknown department')
                response_parts.append(f"**Source {i+1}** ({dept}): {source}\n{doc[:500]}...")
            
            return "\n\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            return f"Error querying knowledge base: {e}. Please check if the vector store exists."

class PrivateGPTQueryTool(BaseTool):
    """Tool for querying the privateGPT knowledge base"""
    
    name: str = "Sales Knowledge Base Query Tool"
    description: str = (
        "Queries the Sales knowledge base (via privateGPT) for specific information. "
        "Use this to find ICP details, sales scripts, email templates, product info, competitor insights, etc. "
        "Input should be a clear, specific question."
    )
    collection_name: Optional[str] = None
    context_filter: Optional[Dict[str, Any]] = None
    client: ClassVar[Any] = None  # Mark as ClassVar to exclude from model fields

    def __init__(self, collection_name: Optional[str] = None, context_filter: Optional[Dict[str, Any]] = None):
        """Initialize the tool with optional collection name and context filter"""
        super().__init__()
        self.collection_name = collection_name or os.getenv("PRIVATE_GPT_COLLECTION_NAME", "documents")
        self.context_filter = context_filter or {}
        # Set the client on the class, not the instance
        if PrivateGPTQueryTool.client is None:
            PrivateGPTQueryTool.client = get_privategpt_client()
        # Set any instance-specific attributes for accessing the class variable
        self._use_mock = os.environ.get('USE_MOCK_KB', 'false').lower() == 'true'
    
    def _run(self, query: str) -> str:
        """Run the query against privateGPT"""
        # Use the class client
        client = PrivateGPTQueryTool.client
        
        # Check if we're in mock mode
        if self._use_mock:
            return f"MOCK KB RESPONSE: Found information about '{query}' in the knowledge base. Here's what I know...\n\nThis is simulated sales knowledge for demonstration purposes."
            
        # Check if privateGPT is running
        if not client.health_check():
            return "Error: privateGPT server is not running. Please start the privateGPT server first."
        
        # Use the client to get a response
        return client.query(query, collection_name=self.collection_name)

# Specialized versions of the PrivateGPTQueryTool for different use cases
class PrivateGPTSalesFullKbTool(PrivateGPTQueryTool):
    """Tool for querying the full sales knowledge base"""
    
    name: str = "Full Sales Knowledge Base Tool"
    description: str = (
        "Queries the entire Sales knowledge base for comprehensive information across all categories. "
        "Use this for high-level strategic questions requiring broad knowledge."
    )
    
    def __init__(self):
        super().__init__(collection_name="documents")
        # Ensure we have the required attributes
        if not hasattr(self, 'collection_name'):
            self.collection_name = os.getenv("PRIVATE_GPT_COLLECTION_NAME", "documents")
        if not hasattr(self, 'context_filter'):
            self.context_filter = {}

class PrivateGPTOutboundSalesPlaybookTool(PrivateGPTQueryTool):
    """Tool for querying outbound sales specific knowledge"""
    
    name: str = "Outbound Sales Playbook Tool"
    description: str = (
        "Queries the Sales knowledge base specifically for outbound sales playbook information. "
        "Use this for outbound strategy, cold outreach tactics, and prospecting guidance."
    )
    
    def __init__(self):
        # In a real implementation, you might filter by folder or tags
        # For now, we'll just rely on query specificity
        super().__init__(collection_name="documents")
        # Ensure we have the required attributes
        if not hasattr(self, 'collection_name'):
            self.collection_name = os.getenv("PRIVATE_GPT_COLLECTION_NAME", "documents")
        if not hasattr(self, 'context_filter'):
            self.context_filter = {}

class PrivateGPTInboundSalesPlaybookTool(PrivateGPTQueryTool):
    """Tool for querying inbound sales specific knowledge"""
    
    name: str = "Inbound Sales Playbook Tool"
    description: str = (
        "Queries the Sales knowledge base specifically for inbound sales playbook information. "
        "Use this for lead nurturing, qualification criteria, and conversion tactics."
    )
    
    def __init__(self):
        # In a real implementation, you might filter by folder or tags
        super().__init__(collection_name="documents")
        # Ensure we have the required attributes
        if not hasattr(self, 'collection_name'):
            self.collection_name = os.getenv("PRIVATE_GPT_COLLECTION_NAME", "documents")
        if not hasattr(self, 'context_filter'):
            self.context_filter = {}

class PrivateGPTSalesICPTool(PrivateGPTQueryTool):
    """Tool for querying Ideal Customer Profile information"""
    
    name: str = "Sales ICP Tool"
    description: str = (
        "Queries the Sales knowledge base specifically for Ideal Customer Profile details. "
        "Use this to understand target customer demographics, firmographics, and qualification criteria."
    )
    
    def __init__(self):
        # You could set a specific context filter to focus on ICP-related documents
        super().__init__(collection_name="documents")
        # Ensure we have the required attributes
        if not hasattr(self, 'collection_name'):
            self.collection_name = os.getenv("PRIVATE_GPT_COLLECTION_NAME", "documents")
        if not hasattr(self, 'context_filter'):
            self.context_filter = {}

class PrivateGPTSalesEmailTemplatesTool(PrivateGPTQueryTool):
    """Tool for querying email templates"""
    
    name: str = "Sales Email Templates Tool"
    description: str = (
        "Queries the Sales knowledge base specifically for email templates and messaging. "
        "Use this to find templates for cold outreach, follow-ups, or specific customer scenarios."
    )
    
    def __init__(self):
        # You could set a specific context filter to focus on template-related documents
        super().__init__(collection_name="documents")
        # Ensure we have the required attributes
        if not hasattr(self, 'collection_name'):
            self.collection_name = os.getenv("PRIVATE_GPT_COLLECTION_NAME", "documents")
        if not hasattr(self, 'context_filter'):
            self.context_filter = {}

class PrivateGPTSalesCRMTool(PrivateGPTQueryTool):
    """Tool for querying CRM best practices and standards"""
    
    name: str = "Sales CRM Tool"
    description: str = (
        "Queries the Sales knowledge base specifically for CRM usage best practices. "
        "Use this to understand data quality standards, required fields, and process documentation."
    )
    
    def __init__(self):
        # You could set a specific context filter to focus on CRM-related documents
        super().__init__(collection_name="documents")
        # Ensure we have the required attributes
        if not hasattr(self, 'collection_name'):
            self.collection_name = os.getenv("PRIVATE_GPT_COLLECTION_NAME", "documents")
        if not hasattr(self, 'context_filter'):
            self.context_filter = {}

# Mock tools for functionality that would connect to external services

class WebSearchTool(BaseTool):
    """Tool for searching the web"""
    
    name: str = "Web Search Tool"
    description: str = (
        "Searches the web for information about companies, trends, or general information. "
        "Input should be a specific search query."
    )
    
    def _run(self, query: str) -> str:
        # This would be implemented with an actual search API like SerperDev or similar
        return f"Mock web search results for: {query}"

class EmailSendingApiTool(BaseTool):
    """Tool for sending emails"""
    
    name: str = "Email Sending API Tool"
    description: str = (
        "Sends an email to a specified recipient. "
        "Input should include recipient, subject, and body."
    )
    
    def _run(self, recipient: str, subject: str, body: str) -> str:
        # This would connect to an actual email sending service
        return f"Mock email sent to {recipient} with subject: {subject}"

class CrmApiTool(BaseTool):
    """Tool for interacting with the CRM API"""
    
    name: str = "CRM API Tool"
    description: str = (
        "Creates, reads, updates, or deletes records in the CRM system. "
        "Input should include the operation and relevant data."
    )
    
    def _run(self, operation: str, data: Dict[str, Any]) -> str:
        # This would connect to an actual CRM API
        return f"Mock CRM API {operation} operation completed with data: {data}"

class SequenceAutomationTool(BaseTool):
    """Tool for automating email sequences"""
    
    name: str = "Sequence Automation Tool"
    description: str = (
        "Creates or updates automated email sequences. "
        "Input should include sequence name, steps, and trigger conditions."
    )
    
    def _run(self, sequence_name: str, steps: List[Dict[str, Any]], triggers: Dict[str, Any]) -> str:
        # This would connect to an actual sequence automation platform
        return f"Mock sequence '{sequence_name}' created/updated with {len(steps)} steps"

class LeadScoringTool(BaseTool):
    """Tool for scoring leads"""
    
    name: str = "Lead Scoring Tool"
    description: str = (
        "Scores leads based on various criteria and returns a prioritized list. "
        "Input should be a list of leads with their attributes."
    )
    
    def _run(self, leads: List[Dict[str, Any]], criteria: Optional[Dict[str, float]] = None) -> str:
        # This would implement a real lead scoring algorithm
        return f"Mock lead scoring completed for {len(leads)} leads based on provided criteria"

# MCP SuperAssistant Tools
class MCPSuperAssistantTool(BaseTool):
    """Generic tool for invoking functions on the MCP-SuperAssistant server"""
    
    name: str = "MCP SuperAssistant Generic Tool"
    description: str = "Invokes a specified function on the MCP-SuperAssistant server."
    mcp_server_url: str = os.getenv("MCP_SERVER_URI", "http://localhost:3006/sse")
    
    def _run(self, mcp_function_name: str, parameters: Dict[str, Any]) -> str:
        """Run a function on the MCP-SuperAssistant server"""
        call_id = str(uuid.uuid4())
        xml_payload = f"<function_calls><invoke name=\"{mcp_function_name}\" call_id=\"{call_id}\">"
        
        for name, value in parameters.items():
            # Basic escaping for XML, consider a proper XML library for complex values
            value_str = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            xml_payload += f"<parameter name=\"{name}\">{value_str}</parameter>"
        
        xml_payload += "</invoke></function_calls>"
        
        logger.info(f"Calling MCP: {mcp_function_name} with payload: {xml_payload}")
        try:
            response = requests.post(
                self.mcp_server_url, 
                data=xml_payload, 
                headers={'Content-Type': 'application/xml'}, 
                timeout=30
            )
            response.raise_for_status()
            
            # Basic extraction (highly dependent on actual MCP response structure)
            logger.info(f"MCP Response: {response.text}")
            if "<tool_output" in response.text and f"call_id=\"{call_id}\"" in response.text:
                # This is a very naive parse, an XML parser would be better
                start_tag = f"<tool_output call_id=\"{call_id}\" name=\"{mcp_function_name}\">"
                end_tag = "</tool_output>"
                start_index = response.text.find(start_tag)
                if start_index != -1:
                    end_index = response.text.find(end_tag, start_index)
                    if end_index != -1:
                        return response.text[start_index + len(start_tag):end_index].strip()
                return f"MCP Success, but result parsing failed. Raw: {response.text}"
            return f"MCP call successful, raw response: {response.text}"
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling MCP SuperAssistant: {e}")
            return f"Error calling MCP SuperAssistant: {e}"

# Specific MCP-backed tools
class WriteFileMCPTool(BaseTool):
    """Tool for writing files via MCP-SuperAssistant"""
    
    name: str = "Write File via MCP"
    description: str = "Creates a new file or overwrites an existing file with new content using MCP-SuperAssistant. Only works within allowed directories."
    mcp_tool_caller: ClassVar[MCPSuperAssistantTool] = None  # Mark as ClassVar to exclude from model fields
    
    def __init__(self):
        super().__init__()
        # Set the tool caller on the class, not the instance
        if WriteFileMCPTool.mcp_tool_caller is None:
            WriteFileMCPTool.mcp_tool_caller = MCPSuperAssistantTool()
    
    def _run(self, path: str, content: str) -> str:
        """Write to a file using MCP-SuperAssistant"""
        parameters = {"path": path, "content": content}
        # Use the class attribute
        caller = WriteFileMCPTool.mcp_tool_caller
        if caller is None:
            return "Mock MCP: File written successfully to " + path
        return caller._run(mcp_function_name="filesystem.write_file", parameters=parameters)

class ReadFileMCPTool(BaseTool):
    """Tool for reading files via MCP-SuperAssistant"""
    
    name: str = "Read File via MCP"
    description: str = "Reads the complete contents of a file from the file system using MCP-SuperAssistant. Only works within allowed directories."
    mcp_tool_caller: ClassVar[MCPSuperAssistantTool] = None  # Mark as ClassVar to exclude from model fields
    
    def __init__(self):
        super().__init__()
        # Set the tool caller on the class, not the instance
        if ReadFileMCPTool.mcp_tool_caller is None:
            ReadFileMCPTool.mcp_tool_caller = MCPSuperAssistantTool()
    
    def _run(self, path: str) -> str:
        """Read a file using MCP-SuperAssistant"""
        parameters = {"path": path}
        # Use the class attribute
        caller = ReadFileMCPTool.mcp_tool_caller
        if caller is None:
            return "Mock MCP: File contents from " + path + "\n\nThis is mock file content for testing purposes."
        return caller._run(mcp_function_name="filesystem.read_file", parameters=parameters)

class ListDirectoryMCPTool(BaseTool):
    """Tool for listing directories via MCP-SuperAssistant"""
    
    name: str = "List Directory via MCP"
    description: str = "Gets a detailed listing of files and directories using MCP-SuperAssistant. Only works within allowed directories."
    mcp_tool_caller: ClassVar[MCPSuperAssistantTool] = None  # Mark as ClassVar to exclude from model fields
    
    def __init__(self):
        super().__init__()
        # Set the tool caller on the class, not the instance
        if ListDirectoryMCPTool.mcp_tool_caller is None:
            ListDirectoryMCPTool.mcp_tool_caller = MCPSuperAssistantTool()
    
    def _run(self, path: str) -> str:
        """List a directory using MCP-SuperAssistant"""
        parameters = {"path": path}
        # Use the class attribute
        caller = ListDirectoryMCPTool.mcp_tool_caller
        if caller is None:
            return "Mock MCP: Directory listing for " + path + "\n\nfile1.txt\nfile2.txt\nsubdir/"
        return caller._run(mcp_function_name="filesystem.list_directory", parameters=parameters)

class SearchFilesMCPTool(BaseTool):
    """Tool for searching files via MCP-SuperAssistant"""
    
    name: str = "Search Files via MCP"
    description: str = "Searches for files matching a pattern using MCP-SuperAssistant. Only works within allowed directories."
    mcp_tool_caller: ClassVar[MCPSuperAssistantTool] = None  # Mark as ClassVar to exclude from model fields
    
    def __init__(self):
        super().__init__()
        # Set the tool caller on the class, not the instance
        if SearchFilesMCPTool.mcp_tool_caller is None:
            SearchFilesMCPTool.mcp_tool_caller = MCPSuperAssistantTool()
    
    def _run(self, pattern: str, path: str = ".") -> str:
        """Search for files using MCP-SuperAssistant"""
        parameters = {"pattern": pattern, "path": path}
        # Use the class attribute
        caller = SearchFilesMCPTool.mcp_tool_caller
        if caller is None:
            return f"Mock MCP: Search results for pattern '{pattern}' in {path}\n\nfound_file1.txt\nfound_file2.txt"
        return caller._run(mcp_function_name="filesystem.search_files", parameters=parameters)

class CreateDirectoryMCPTool(BaseTool):
    """Tool for creating directories via MCP-SuperAssistant"""
    
    name: str = "Create Directory via MCP"
    description: str = "Creates a new directory using MCP-SuperAssistant. Only works within allowed directories."
    mcp_tool_caller: ClassVar[MCPSuperAssistantTool] = None  # Mark as ClassVar to exclude from model fields
    
    def __init__(self):
        super().__init__()
        # Set the tool caller on the class, not the instance
        if CreateDirectoryMCPTool.mcp_tool_caller is None:
            CreateDirectoryMCPTool.mcp_tool_caller = MCPSuperAssistantTool()
    
    def _run(self, path: str) -> str:
        """Create a directory using MCP-SuperAssistant"""
        parameters = {"path": path}
        # Use the class attribute
        caller = CreateDirectoryMCPTool.mcp_tool_caller
        if caller is None:
            return "Mock MCP: Directory created successfully at " + path
        return caller._run(mcp_function_name="filesystem.create_directory", parameters=parameters)

# MCP Tool Classes for All Departments

# Administrative Department Tools
class MCPCalendarReadTool(MCPSuperAssistantTool):
    name: str = "MCP Calendar Read Tool"
    description: str = "Reads calendar events and availability via MCP-SuperAssistant"
    
    def _run(self, calendar_id: str = "primary", start_date: str = "", end_date: str = "") -> str:
        parameters = {"calendar_id": calendar_id, "start_date": start_date, "end_date": end_date}
        return super()._run("calendar.read_events", parameters)

class MCPCalendarWriteTool(MCPSuperAssistantTool):
    name: str = "MCP Calendar Write Tool"
    description: str = "Creates or updates calendar events via MCP-SuperAssistant"
    
    def _run(self, title: str, start_time: str, end_time: str, attendees: str = "") -> str:
        parameters = {"title": title, "start_time": start_time, "end_time": end_time, "attendees": attendees}
        return super()._run("calendar.create_event", parameters)

class MCPEmailReadTool(MCPSuperAssistantTool):
    name: str = "MCP Email Read Tool"
    description: str = "Reads emails from inbox via MCP-SuperAssistant"
    
    def _run(self, folder: str = "inbox", limit: int = 10) -> str:
        parameters = {"folder": folder, "limit": str(limit)}
        return super()._run("email.read_messages", parameters)

class MCPEmailSendTool(MCPSuperAssistantTool):
    name: str = "MCP Email Send Tool"
    description: str = "Sends emails via MCP-SuperAssistant"
    
    def _run(self, to: str, subject: str, body: str, cc: str = "") -> str:
        parameters = {"to": to, "subject": subject, "body": body, "cc": cc}
        return super()._run("email.send_message", parameters)

class MCPFileOrganizationTool(MCPSuperAssistantTool):
    name: str = "MCP File Organization Tool"
    description: str = "Organizes files and folders via MCP-SuperAssistant"
    
    def _run(self, source_path: str, destination_path: str, operation: str = "move") -> str:
        parameters = {"source_path": source_path, "destination_path": destination_path, "operation": operation}
        return super()._run("filesystem.organize_files", parameters)

class MCPNotionAdminDocsTool(MCPSuperAssistantTool):
    name: str = "MCP Notion Admin Docs Tool"
    description: str = "Manages administrative documentation in Notion via MCP-SuperAssistant"
    
    def _run(self, page_id: str, content: str = "", operation: str = "read") -> str:
        parameters = {"page_id": page_id, "content": content, "operation": operation}
        return super()._run("notion.manage_page", parameters)

class MCPTaskAssignmentTool(MCPSuperAssistantTool):
    name: str = "MCP Task Assignment Tool"
    description: str = "Assigns tasks to team members via MCP-SuperAssistant"
    
    def _run(self, assignee: str, task_title: str, description: str, due_date: str = "") -> str:
        parameters = {"assignee": assignee, "task_title": task_title, "description": description, "due_date": due_date}
        return super()._run("tasks.assign_task", parameters)

class MCPGoogleCalendarReadTool(MCPCalendarReadTool):
    name: str = "MCP Google Calendar Read Tool"
    description: str = "Reads Google Calendar events via MCP-SuperAssistant"

class MCPGoogleCalendarWriteTool(MCPCalendarWriteTool):
    name: str = "MCP Google Calendar Write Tool"
    description: str = "Creates Google Calendar events via MCP-SuperAssistant"

class MCPTravelBookingTool(MCPSuperAssistantTool):
    name: str = "MCP Travel Booking Tool"
    description: str = "Books travel arrangements via MCP-SuperAssistant"
    
    def _run(self, traveler: str, departure: str, destination: str, dates: str) -> str:
        parameters = {"traveler": traveler, "departure": departure, "destination": destination, "dates": dates}
        return super()._run("travel.book_travel", parameters)

class MCPTaskDelegationTool(MCPSuperAssistantTool):
    name: str = "MCP Task Delegation Tool"
    description: str = "Delegates tasks between agents via MCP-SuperAssistant"
    
    def _run(self, from_agent: str, to_agent: str, task_description: str, priority: str = "medium") -> str:
        parameters = {"from_agent": from_agent, "to_agent": to_agent, "task_description": task_description, "priority": priority}
        return super()._run("agents.delegate_task", parameters)

class MCPVendorDirectoryTool(MCPSuperAssistantTool):
    name: str = "MCP Vendor Directory Tool"
    description: str = "Manages vendor directory and contacts via MCP-SuperAssistant"
    
    def _run(self, vendor_name: str, operation: str = "search", contact_info: str = "") -> str:
        parameters = {"vendor_name": vendor_name, "operation": operation, "contact_info": contact_info}
        return super()._run("vendors.manage_directory", parameters)

class MCPMeetingRoomBookingTool(MCPSuperAssistantTool):
    name: str = "MCP Meeting Room Booking Tool"
    description: str = "Books meeting rooms via MCP-SuperAssistant"
    
    def _run(self, room_name: str, start_time: str, end_time: str, attendees: str = "") -> str:
        parameters = {"room_name": room_name, "start_time": start_time, "end_time": end_time, "attendees": attendees}
        return super()._run("facilities.book_room", parameters)

class MCPAvailabilityCheckerTool(MCPSuperAssistantTool):
    name: str = "MCP Availability Checker Tool"
    description: str = "Checks availability for people and resources via MCP-SuperAssistant"
    
    def _run(self, resource_type: str, resource_id: str, time_range: str) -> str:
        parameters = {"resource_type": resource_type, "resource_id": resource_id, "time_range": time_range}
        return super()._run("availability.check_availability", parameters)

class MCPCalendarConflictResolverTool(MCPSuperAssistantTool):
    name: str = "MCP Calendar Conflict Resolver Tool"
    description: str = "Resolves calendar conflicts and suggests alternatives via MCP-SuperAssistant"
    
    def _run(self, event_id: str, attendees: str, preferred_times: str) -> str:
        parameters = {"event_id": event_id, "attendees": attendees, "preferred_times": preferred_times}
        return super()._run("calendar.resolve_conflicts", parameters)

# Marketing Department Tools
class MCPContentStorageTool(MCPSuperAssistantTool):
    name: str = "MCP Content Storage Tool"
    description: str = "Manages content storage and organization via MCP-SuperAssistant"
    
    def _run(self, content_type: str, content_data: str, tags: str = "", operation: str = "store") -> str:
        parameters = {"content_type": content_type, "content_data": content_data, "tags": tags, "operation": operation}
        return super()._run("content.manage_storage", parameters)

class MCPNotionContentDocsTool(MCPSuperAssistantTool):
    name: str = "MCP Notion Content Docs Tool"
    description: str = "Manages content documentation in Notion via MCP-SuperAssistant"
    
    def _run(self, page_id: str, content: str = "", operation: str = "read") -> str:
        parameters = {"page_id": page_id, "content": content, "operation": operation}
        return super()._run("notion.manage_content_page", parameters)

class MCPAnalyticsApiTool(MCPSuperAssistantTool):
    name: str = "MCP Analytics API Tool"
    description: str = "Retrieves marketing analytics data via MCP-SuperAssistant"
    
    def _run(self, metric_type: str, date_range: str, filters: str = "") -> str:
        parameters = {"metric_type": metric_type, "date_range": date_range, "filters": filters}
        return super()._run("analytics.get_metrics", parameters)

class MCPContentCalendarTool(MCPSuperAssistantTool):
    name: str = "MCP Content Calendar Tool"
    description: str = "Manages content calendar and scheduling via MCP-SuperAssistant"
    
    def _run(self, operation: str, content_title: str = "", publish_date: str = "", content_type: str = "") -> str:
        parameters = {"operation": operation, "content_title": content_title, "publish_date": publish_date, "content_type": content_type}
        return super()._run("content.manage_calendar", parameters)

class MCPSEOAnalysisTool(MCPSuperAssistantTool):
    name: str = "MCP SEO Analysis Tool"
    description: str = "Performs SEO analysis and optimization via MCP-SuperAssistant"
    
    def _run(self, url: str, keywords: str = "", analysis_type: str = "full") -> str:
        parameters = {"url": url, "keywords": keywords, "analysis_type": analysis_type}
        return super()._run("seo.analyze_content", parameters)

class MCPVideoProjectFileTool(MCPSuperAssistantTool):
    name: str = "MCP Video Project File Tool"
    description: str = "Manages video project files via MCP-SuperAssistant"
    
    def _run(self, project_name: str, file_path: str, operation: str = "read") -> str:
        parameters = {"project_name": project_name, "file_path": file_path, "operation": operation}
        return super()._run("video.manage_project_files", parameters)

class MCPVideoMetadataTool(MCPSuperAssistantTool):
    name: str = "MCP Video Metadata Tool"
    description: str = "Manages video metadata and tags via MCP-SuperAssistant"
    
    def _run(self, video_id: str, metadata: str = "", operation: str = "read") -> str:
        parameters = {"video_id": video_id, "metadata": metadata, "operation": operation}
        return super()._run("video.manage_metadata", parameters)

class MCPSocialMediaPublishingTool(MCPSuperAssistantTool):
    name: str = "MCP Social Media Publishing Tool"
    description: str = "Publishes content to social media platforms via MCP-SuperAssistant"
    
    def _run(self, platform: str, content: str, media_url: str = "", schedule_time: str = "") -> str:
        parameters = {"platform": platform, "content": content, "media_url": media_url, "schedule_time": schedule_time}
        return super()._run("social.publish_content", parameters)

class MCPAssetLibraryTool(MCPSuperAssistantTool):
    name: str = "MCP Asset Library Tool"
    description: str = "Manages digital asset library via MCP-SuperAssistant"
    
    def _run(self, asset_type: str, search_terms: str = "", operation: str = "search") -> str:
        parameters = {"asset_type": asset_type, "search_terms": search_terms, "operation": operation}
        return super()._run("assets.manage_library", parameters)

class MCPWebSearchTool(MCPSuperAssistantTool):
    name: str = "MCP Web Search Tool"
    description: str = "Performs web searches via MCP-SuperAssistant"
    
    def _run(self, query: str, result_count: int = 10, site_filter: str = "") -> str:
        parameters = {"query": query, "result_count": str(result_count), "site_filter": site_filter}
        return super()._run("web.search", parameters)

class MCPIdeaLoggingTool(MCPSuperAssistantTool):
    name: str = "MCP Idea Logging Tool"
    description: str = "Logs and organizes content ideas via MCP-SuperAssistant"
    
    def _run(self, idea_title: str, description: str, category: str = "", priority: str = "medium") -> str:
        parameters = {"idea_title": idea_title, "description": description, "category": category, "priority": priority}
        return super()._run("ideas.log_idea", parameters)

class MCPCampaignDocsTool(MCPSuperAssistantTool):
    name: str = "MCP Campaign Docs Tool"
    description: str = "Manages campaign documentation via MCP-SuperAssistant"
    
    def _run(self, campaign_name: str, doc_type: str, content: str = "", operation: str = "read") -> str:
        parameters = {"campaign_name": campaign_name, "doc_type": doc_type, "content": content, "operation": operation}
        return super()._run("campaigns.manage_docs", parameters)

class MCPKeywordResearchTool(MCPSuperAssistantTool):
    name: str = "MCP Keyword Research Tool"
    description: str = "Performs keyword research and analysis via MCP-SuperAssistant"
    
    def _run(self, seed_keywords: str, market: str = "US", language: str = "en") -> str:
        parameters = {"seed_keywords": seed_keywords, "market": market, "language": language}
        return super()._run("seo.keyword_research", parameters)

# Engineering Department Tools
class MCPCodeRepositoryTool(MCPSuperAssistantTool):
    name: str = "MCP Code Repository Tool"
    description: str = "Manages code repositories via MCP-SuperAssistant"
    
    def _run(self, repo_name: str, operation: str, branch: str = "main", file_path: str = "") -> str:
        parameters = {"repo_name": repo_name, "operation": operation, "branch": branch, "file_path": file_path}
        return super()._run("git.manage_repository", parameters)

class MCPCICDTriggerTool(MCPSuperAssistantTool):
    name: str = "MCP CI/CD Trigger Tool"
    description: str = "Triggers CI/CD pipelines via MCP-SuperAssistant"
    
    def _run(self, pipeline_name: str, branch: str = "main", parameters_json: str = "{}") -> str:
        parameters = {"pipeline_name": pipeline_name, "branch": branch, "parameters": parameters_json}
        return super()._run("cicd.trigger_pipeline", parameters)

class MCPBugTrackerTool(MCPSuperAssistantTool):
    name: str = "MCP Bug Tracker Tool"
    description: str = "Manages bug tracking system via MCP-SuperAssistant"
    
    def _run(self, operation: str, bug_id: str = "", title: str = "", description: str = "") -> str:
        parameters = {"operation": operation, "bug_id": bug_id, "title": title, "description": description}
        return super()._run("bugs.manage_tickets", parameters)

class MCPProjectManagementApiTool(MCPSuperAssistantTool):
    name: str = "MCP Project Management API Tool"
    description: str = "Manages projects via MCP-SuperAssistant"
    
    def _run(self, project_id: str, operation: str, task_data: str = "") -> str:
        parameters = {"project_id": project_id, "operation": operation, "task_data": task_data}
        return super()._run("projects.manage_tasks", parameters)

class MCPDocumentationReaderTool(MCPSuperAssistantTool):
    name: str = "MCP Documentation Reader Tool"
    description: str = "Reads technical documentation via MCP-SuperAssistant"
    
    def _run(self, doc_type: str, search_terms: str = "", section: str = "") -> str:
        parameters = {"doc_type": doc_type, "search_terms": search_terms, "section": section}
        return super()._run("docs.read_documentation", parameters)

# Finance Department Tools
class MCPAccountingSoftwareApiTool(MCPSuperAssistantTool):
    name: str = "MCP Accounting Software API Tool"
    description: str = "Manages accounting records via MCP-SuperAssistant"
    
    def _run(self, operation: str, account_id: str = "", transaction_data: str = "") -> str:
        parameters = {"operation": operation, "account_id": account_id, "transaction_data": transaction_data}
        return super()._run("accounting.manage_records", parameters)

class MCPFinancialReportWriterTool(MCPSuperAssistantTool):
    name: str = "MCP Financial Report Writer Tool"
    description: str = "Generates financial reports via MCP-SuperAssistant"
    
    def _run(self, report_type: str, date_range: str, format_type: str = "pdf") -> str:
        parameters = {"report_type": report_type, "date_range": date_range, "format": format_type}
        return super()._run("finance.generate_report", parameters)

class MCPPayrollManagementTool(MCPSuperAssistantTool):
    name: str = "MCP Payroll Management Tool"
    description: str = "Manages payroll operations via MCP-SuperAssistant"
    
    def _run(self, operation: str, employee_id: str = "", payroll_data: str = "") -> str:
        parameters = {"operation": operation, "employee_id": employee_id, "payroll_data": payroll_data}
        return super()._run("payroll.manage_payroll", parameters)

class MCPInvoiceGeneratorTool(MCPSuperAssistantTool):
    name: str = "MCP Invoice Generator Tool"
    description: str = "Generates invoices via MCP-SuperAssistant"
    
    def _run(self, customer_id: str, items: str, due_date: str = "") -> str:
        parameters = {"customer_id": customer_id, "items": items, "due_date": due_date}
        return super()._run("billing.generate_invoice", parameters)

class MCPExpenseTrackingTool(MCPSuperAssistantTool):
    name: str = "MCP Expense Tracking Tool"
    description: str = "Tracks expenses via MCP-SuperAssistant"
    
    def _run(self, operation: str, expense_data: str = "", employee_id: str = "") -> str:
        parameters = {"operation": operation, "expense_data": expense_data, "employee_id": employee_id}
        return super()._run("expenses.track_expenses", parameters)

# Customer Department Tools
class MCPCRMApiTool(MCPSuperAssistantTool):
    name: str = "MCP CRM API Tool"
    description: str = "Manages customer records via MCP-SuperAssistant"
    
    def _run(self, operation: str, customer_id: str = "", customer_data: str = "") -> str:
        parameters = {"operation": operation, "customer_id": customer_id, "customer_data": customer_data}
        return super()._run("crm.manage_customers", parameters)

class MCPSupportTicketingApiTool(MCPSuperAssistantTool):
    name: str = "MCP Support Ticketing API Tool"
    description: str = "Manages support tickets via MCP-SuperAssistant"
    
    def _run(self, operation: str, ticket_id: str = "", ticket_data: str = "") -> str:
        parameters = {"operation": operation, "ticket_id": ticket_id, "ticket_data": ticket_data}
        return super()._run("support.manage_tickets", parameters)

class MCPReportWriterTool(MCPSuperAssistantTool):
    name: str = "MCP Report Writer Tool"
    description: str = "Generates customer reports via MCP-SuperAssistant"
    
    def _run(self, report_type: str, date_range: str, filters: str = "") -> str:
        parameters = {"report_type": report_type, "date_range": date_range, "filters": filters}
        return super()._run("reports.generate_customer_report", parameters)

class MCPCommunityPlatformTool(MCPSuperAssistantTool):
    name: str = "MCP Community Platform Tool"
    description: str = "Manages community platform via MCP-SuperAssistant"
    
    def _run(self, operation: str, user_id: str = "", content: str = "") -> str:
        parameters = {"operation": operation, "user_id": user_id, "content": content}
        return super()._run("community.manage_platform", parameters)

# Department-specific Knowledge Base Tools (Direct RAG)
class AdminKBTool(KnowledgeBaseTool):
    name: str = "Admin Knowledge Base Tool"
    description: str = "Queries the Admin knowledge base for policies, procedures, and guidelines"
    
    def __init__(self):
        super().__init__(department_filter="admin")

class MarketingKBTool(KnowledgeBaseTool):
    name: str = "Marketing Knowledge Base Tool"
    description: str = "Queries the Marketing knowledge base for brand guidelines, strategies, and best practices"
    
    def __init__(self):
        super().__init__(department_filter="marketing")

class ProductKBTool(KnowledgeBaseTool):
    name: str = "Product Knowledge Base Tool"
    description: str = "Queries the Product knowledge base for coding standards, architecture, and technical documentation"
    
    def __init__(self):
        super().__init__(department_filter="product")

class BackOfficeKBTool(KnowledgeBaseTool):
    name: str = "Back Office Knowledge Base Tool"
    description: str = "Queries the Back Office knowledge base for accounting policies, procedures, and compliance guidelines"
    
    def __init__(self):
        super().__init__(department_filter="back_office")

class CustomerKBTool(KnowledgeBaseTool):
    name: str = "Customer Knowledge Base Tool"
    description: str = "Queries the Customer knowledge base for support playbooks, success metrics, and guidelines"
    
    def __init__(self):
        super().__init__(department_filter="customer")

class SalesKBTool(KnowledgeBaseTool):
    name: str = "Sales Knowledge Base Tool"
    description: str = "Queries the Sales knowledge base for ICP details, scripts, templates, and processes"
    
    def __init__(self):
        super().__init__(department_filter="sales_docs")

class SecurityKBTool(KnowledgeBaseTool):
    name: str = "Security Knowledge Base Tool"
    description: str = (
        "Queries the Security knowledge base for policies, compliance requirements, "
        "incident response procedures, risk management, and security guidelines."
    )
    
    def __init__(self):
        super().__init__(department_filter="security")

# Legacy PrivateGPT tools (maintained for backward compatibility)
class PrivateGPTAdminKBTool(PrivateGPTQueryTool):
    name: str = "Admin Knowledge Base Tool (Legacy)"
    description: str = "Queries the Admin knowledge base for policies, procedures, and guidelines"
    
    def __init__(self):
        super().__init__(collection_name="admin_documents")

class PrivateGPTMarketingKBTool(PrivateGPTQueryTool):
    name: str = "Marketing Knowledge Base Tool (Legacy)"
    description: str = "Queries the Marketing knowledge base for brand guidelines, strategies, and best practices"
    
    def __init__(self):
        super().__init__(collection_name="marketing_documents")

class PrivateGPTMarketingTrendsTool(PrivateGPTQueryTool):
    name: str = "Marketing Trends Knowledge Base Tool (Legacy)"
    description: str = "Queries the Marketing knowledge base specifically for trends and market insights"
    
    def __init__(self):
        super().__init__(collection_name="marketing_trends")

class PrivateGPTProductKBTool(PrivateGPTQueryTool):
    name: str = "Product Knowledge Base Tool (Legacy)"
    description: str = "Queries the Product knowledge base for coding standards, architecture, and technical documentation"
    
    def __init__(self):
        super().__init__(collection_name="product_documents")

class PrivateGPTBackOfficeKBTool(PrivateGPTQueryTool):
    name: str = "Back Office Knowledge Base Tool (Legacy)"
    description: str = "Queries the Back Office knowledge base for accounting policies, procedures, and compliance guidelines"
    
    def __init__(self):
        super().__init__(collection_name="back_office_documents")

class PrivateGPTCustomerKBTool(PrivateGPTQueryTool):
    name: str = "Customer Knowledge Base Tool (Legacy)"
    description: str = "Queries the Customer knowledge base for support playbooks, success metrics, and guidelines"
    
    def __init__(self):
        super().__init__(collection_name="customer_documents")

class PrivateGPTSecurityKBTool(PrivateGPTQueryTool):
    """Tool for querying the Security department knowledge base (Legacy)"""
    
    name: str = "Security Knowledge Base Tool (Legacy)"
    description: str = (
        "Queries the Security knowledge base for policies, compliance requirements, "
        "incident response procedures, risk management, and security guidelines."
    )
    
    def __init__(self):
        super().__init__(collection_name="security_documents")

# Sales Department MCP Tools for MVP Use Cases
class MCPNotionCRMTool(MCPSuperAssistantTool):
    name: str = "MCP Notion CRM Tool"
    description: str = "Manages CRM operations in Notion including leads, deals, and pipeline data"
    
    def _run(self, operation: str, entity_type: str = "contact", entity_id: str = "", data: str = "") -> str:
        parameters = {"operation": operation, "entity_type": entity_type, "entity_id": entity_id, "data": data}
        return super()._run("notion.crm_operations", parameters)

class MCPNotionQueryDBTool(MCPSuperAssistantTool):
    name: str = "MCP Notion Query Database Tool"
    description: str = "Queries Notion databases for specific records and data"
    
    def _run(self, database_id: str, filters: str = "", sorts: str = "", limit: int = 50) -> str:
        parameters = {"database_id": database_id, "filters": filters, "sorts": sorts, "limit": str(limit)}
        return super()._run("notion.query_database", parameters)

class MCPNotionCreateContactTool(MCPSuperAssistantTool):
    name: str = "MCP Notion Create Contact Tool"
    description: str = "Creates new contacts/leads in Notion CRM database"
    
    def _run(self, name: str, email: str, company: str = "", phone: str = "", status: str = "New Lead") -> str:
        parameters = {"name": name, "email": email, "company": company, "phone": phone, "status": status}
        return super()._run("notion.create_contact", parameters)

class MCPNotionUpdateContactTool(MCPSuperAssistantTool):
    name: str = "MCP Notion Update Contact Tool"
    description: str = "Updates existing contacts/leads in Notion CRM database"
    
    def _run(self, contact_id: str, updates: str) -> str:
        parameters = {"contact_id": contact_id, "updates": updates}
        return super()._run("notion.update_contact", parameters)

class MCPNotionLogActivityTool(MCPSuperAssistantTool):
    name: str = "MCP Notion Log Activity Tool"
    description: str = "Logs sales activities and interactions in Notion CRM"
    
    def _run(self, contact_id: str, activity_type: str, description: str, date: str = "") -> str:
        parameters = {"contact_id": contact_id, "activity_type": activity_type, "description": description, "date": date}
        return super()._run("notion.log_activity", parameters)

class MCPNotionPipelineTool(MCPSuperAssistantTool):
    name: str = "MCP Notion Pipeline Tool"
    description: str = "Manages sales pipeline stages and deal progression in Notion"
    
    def _run(self, deal_id: str = "", stage: str = "", operation: str = "view", deal_data: str = "") -> str:
        parameters = {"deal_id": deal_id, "stage": stage, "operation": operation, "deal_data": deal_data}
        return super()._run("notion.manage_pipeline", parameters)

class MCPGmailSendTool(MCPSuperAssistantTool):
    name: str = "MCP Gmail Send Tool"
    description: str = "Sends emails via Gmail through MCP-SuperAssistant"
    
    def _run(self, to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
        parameters = {"to": to, "subject": subject, "body": body, "cc": cc, "bcc": bcc}
        return super()._run("gmail.send_email", parameters)

class MCPGmailSearchTool(MCPSuperAssistantTool):
    name: str = "MCP Gmail Search Tool"
    description: str = "Searches Gmail for specific emails and threads"
    
    def _run(self, query: str, max_results: int = 10) -> str:
        parameters = {"query": query, "max_results": str(max_results)}
        return super()._run("gmail.search_emails", parameters)

class MCPWebSearchTool(MCPSuperAssistantTool):
    name: str = "MCP Web Search Tool"
    description: str = "Performs web searches for lead research and company information"

    def _run(self, query: str, site: str = "", num_results: int = 10) -> str:
        parameters = {"query": query, "site": site, "num_results": str(num_results)}
        return super()._run("web.search", parameters)


# ============================================================
# n8n MCP Integration Tools
# ============================================================

class N8NMCPTool(BaseTool):
    """
    Base tool for interacting with n8n workflows via MCP protocol.
    Connects to n8n's Instance-level MCP server (JSON-RPC over HTTP).

    n8n MCP Server URL format: https://your-instance.app.n8n.cloud/mcp-server/http
    Authentication: Bearer token (N8N_MCP_TOKEN from n8n Instance-level MCP settings)
    """
    name: str = "n8n MCP Base Tool"
    description: str = "Base class for n8n MCP integration tools"
    n8n_mcp_url: str = os.getenv("N8N_MCP_SERVER_URI", "https://localhost/mcp-server/http")
    n8n_mcp_token: str = os.getenv("N8N_MCP_TOKEN", "")
    n8n_host: str = os.getenv("N8N_HOST", "https://localhost")

    def _run(self, method: str, params: Dict[str, Any]) -> str:
        """Execute an n8n operation via MCP protocol (JSON-RPC over HTTP)"""
        request_id = str(uuid.uuid4())

        # n8n MCP uses JSON-RPC 2.0 format
        json_rpc_payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'  # n8n MCP requires SSE support
        }

        # Add Bearer token authentication
        if self.n8n_mcp_token:
            headers['Authorization'] = f'Bearer {self.n8n_mcp_token}'

        logger.info(f"Calling n8n MCP: {method}")
        try:
            response = requests.post(
                self.n8n_mcp_url,
                json=json_rpc_payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()

            # n8n MCP returns SSE format: "event: message\ndata: {...}"
            response_text = response.text
            result_data = None

            # Parse SSE format
            for line in response_text.split('\n'):
                if line.startswith('data: '):
                    try:
                        result_data = json.loads(line[6:])  # Skip "data: " prefix
                        break
                    except json.JSONDecodeError:
                        continue

            if result_data is None:
                # Try parsing as regular JSON
                try:
                    result_data = response.json()
                except json.JSONDecodeError:
                    return f"Could not parse n8n MCP response: {response_text[:200]}"

            logger.info(f"n8n MCP Response: {json.dumps(result_data)[:200]}...")

            if "error" in result_data:
                return f"n8n MCP Error: {result_data['error']}"

            return json.dumps(result_data.get("result", result_data))
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling n8n MCP: {e}")
            return f"Error calling n8n MCP: {e}"

    def list_tools(self) -> str:
        """List available tools/workflows from n8n MCP server"""
        return self._run("tools/list", {})

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a specific tool exposed by n8n MCP"""
        return self._run("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })


class N8NTriggerWorkflowTool(N8NMCPTool):
    """Tool for executing n8n workflows via MCP"""
    name: str = "n8n Execute Workflow Tool"
    description: str = (
        "Executes an n8n workflow by ID. First use search_workflows to find "
        "workflows, then get_workflow_details for input schema."
    )

    def _run(self, workflow_id: str, input_data: Optional[Dict[str, Any]] = None) -> str:
        """Execute an n8n workflow via MCP"""
        return self.call_tool("execute_workflow", {
            "workflowId": workflow_id,
            "inputData": input_data or {}
        })


class N8NListWorkflowsTool(N8NMCPTool):
    """Tool for searching n8n workflows via MCP"""
    name: str = "n8n Search Workflows Tool"
    description: str = (
        "Searches for n8n workflows. Use query parameter to filter by name/description."
    )

    def _run(self, query: str = "", limit: int = 50) -> str:
        """Search n8n workflows via MCP"""
        return self.call_tool("search_workflows", {
            "query": query,
            "limit": limit
        })


class N8NGetWorkflowDetailsTool(N8NMCPTool):
    """Tool for getting detailed information about an n8n workflow"""
    name: str = "n8n Get Workflow Details Tool"
    description: str = (
        "Gets detailed information about a workflow including trigger details "
        "and input schema. Use this before executing a workflow."
    )

    def _run(self, workflow_id: str) -> str:
        """Get workflow details via MCP"""
        return self.call_tool("get_workflow_details", {
            "workflowId": workflow_id
        })


class N8NSalesAutomationTool(N8NMCPTool):
    """
    Tool for triggering sales-specific n8n workflows via MCP.
    Discovers and calls sales workflows exposed by n8n MCP server.
    """
    name: str = "n8n Sales Automation Tool"
    description: str = (
        "Triggers sales automation workflows in n8n via MCP. "
        "First use list_tools() to discover available sales workflows, "
        "then call them with appropriate data."
    )

    def _run(self, workflow_name: str, lead_data: Dict[str, Any]) -> str:
        """Trigger a sales workflow via n8n MCP"""
        # Call the workflow tool directly via MCP
        return self.call_tool(workflow_name, {
            "action": "sales",
            "data": lead_data
        })

    def discover_sales_workflows(self) -> str:
        """Discover available sales workflows from n8n MCP"""
        tools_response = self.list_tools()
        # Filter for sales-related tools if possible
        return tools_response


class N8NMarketingAutomationTool(N8NMCPTool):
    """
    Tool for triggering marketing-specific n8n workflows via MCP.
    Discovers and calls marketing workflows exposed by n8n MCP server.
    """
    name: str = "n8n Marketing Automation Tool"
    description: str = (
        "Triggers marketing automation workflows in n8n via MCP. "
        "First use list_tools() to discover available marketing workflows, "
        "then call them with appropriate data."
    )

    def _run(self, workflow_name: str, campaign_data: Dict[str, Any]) -> str:
        """Trigger a marketing workflow via n8n MCP"""
        return self.call_tool(workflow_name, {
            "action": "marketing",
            "data": campaign_data
        })

    def discover_marketing_workflows(self) -> str:
        """Discover available marketing workflows from n8n MCP"""
        tools_response = self.list_tools()
        return tools_response


class N8NExecuteWorkflowTool(N8NMCPTool):
    """
    Tool for executing any n8n workflow exposed via MCP.
    Use list_tools() first to discover available workflows.
    """
    name: str = "n8n Execute Workflow Tool"
    description: str = (
        "Executes any n8n workflow exposed via MCP. "
        "Use list_tools() to discover available workflows first."
    )

    def _run(self, workflow_name: str, input_data: Dict[str, Any]) -> str:
        """Execute a workflow via n8n MCP"""
        return self.call_tool(workflow_name, input_data)


# Check if we're in mock mode
USE_MOCK_KB = os.environ.get('USE_MOCK_KB', 'false').lower() == 'true'

# Create a simple mock tool function that doesn't depend on CrewAI
def create_mock_tool(tool_name: str, tool_description: str, func: Optional[Callable] = None) -> Dict[str, Any]:
    """Create a mock tool that works with CrewAI or without it"""
    if not func:
        func = lambda x: f"Mock response from {tool_name} tool: Processed your request about '{x[:30]}...'"
    
    # If CrewAI BaseTool is available, create a simple custom tool
    if CREWAI_AVAILABLE:
        # Define a simple subclass of BaseTool that works
        class SimpleTool(BaseTool):
            name: str = tool_name
            description: str = tool_description
            
            def _run(self, *args, **kwargs):
                # Join all args and kwargs into a string for the mock function
                input_str = " ".join([str(a) for a in args])
                for k, v in kwargs.items():
                    input_str += f" {k}={v}"
                return func(input_str)
        
        try:
            return SimpleTool()
        except Exception as e:
            print(f"Error creating BaseTool: {e}, falling back to dict format")
    
    # Fallback to dictionary format
    return {
        "name": tool_name,
        "description": tool_description,
        "func": func
    }

# Tool factory function to create tool instances by name
def get_tool_by_name(tool_name: str) -> Optional[Any]:
    """Get a tool instance by its name"""
    
    # If we're in mock mode, return mock tools for everything
    if USE_MOCK_KB:
        # Return mock tools with appropriate names and descriptions
        mock_tools = {
            "private_gpt_sales_full_kb_tool": create_mock_tool(
                "Full Sales Knowledge Base Tool",
                "Queries the entire Sales knowledge base for comprehensive information."
            ),
            "private_gpt_outbound_sales_playbook_tool": create_mock_tool(
                "Outbound Sales Playbook Tool",
                "Provides outbound sales strategies and tactics."
            ),
            "private_gpt_inbound_sales_playbook_tool": create_mock_tool(
                "Inbound Sales Playbook Tool",
                "Provides inbound sales strategies and lead nurturing tactics."
            ),
            "private_gpt_sales_icp_tool": create_mock_tool(
                "Sales ICP Tool",
                "Provides information about Ideal Customer Profiles."
            ),
            "private_gpt_sales_email_templates_tool": create_mock_tool(
                "Sales Email Templates Tool",
                "Retrieves email templates for various sales scenarios."
            ),
            "private_gpt_sales_crm_tool": create_mock_tool(
                "Sales CRM Tool",
                "Provides best practices for CRM usage in sales."
            ),
            "web_search_tool": create_mock_tool(
                "Web Search Tool",
                "Searches the web for information."
            ),
            "email_sending_api_tool": create_mock_tool(
                "Email Sending API Tool",
                "Sends emails to specified recipients."
            ),
            "crm_api_tool": create_mock_tool(
                "CRM API Tool",
                "Interacts with the CRM API to manage records."
            ),
            "sequence_automation_tool": create_mock_tool(
                "Sequence Automation Tool",
                "Creates or updates automated email sequences."
            ),
            "lead_scoring_tool": create_mock_tool(
                "Lead Scoring Tool",
                "Scores leads based on various criteria."
            ),
            "mcp_write_file": create_mock_tool(
                "Write File via MCP",
                "Creates or overwrites files using MCP-SuperAssistant."
            ),
            "mcp_read_file": create_mock_tool(
                "Read File via MCP",
                "Reads file contents using MCP-SuperAssistant."
            ),
            "mcp_list_directory": create_mock_tool(
                "List Directory via MCP",
                "Lists directory contents using MCP-SuperAssistant."
            ),
            "mcp_search_files": create_mock_tool(
                "Search Files via MCP",
                "Searches for files using MCP-SuperAssistant."
            ),
            "mcp_create_directory": create_mock_tool(
                "Create Directory via MCP",
                "Creates directories using MCP-SuperAssistant."
            ),
            "delegation_tool": create_mock_tool(
                "Delegation Tool",
                "Delegates tasks to other agents."
            ),
            "reporting_tool": create_mock_tool(
                "Reporting Tool",
                "Creates and sends reports."
            ),
            # Sales MVP MCP Tools
            "mcp_notion_crm_tool": create_mock_tool(
                "Mock Notion CRM Tool",
                "Mock CRM operations in Notion for MVP testing"
            ),
            "mcp_notion_query_db_tool": create_mock_tool(
                "Mock Notion Query Database Tool",
                "Mock database queries in Notion for MVP testing"
            ),
            "mcp_notion_create_contact_tool": create_mock_tool(
                "Mock Notion Create Contact Tool",
                "Mock contact creation in Notion for MVP testing"
            ),
            "mcp_notion_update_contact_tool": create_mock_tool(
                "Mock Notion Update Contact Tool",
                "Mock contact updates in Notion for MVP testing"
            ),
            "mcp_notion_log_activity_tool": create_mock_tool(
                "Mock Notion Log Activity Tool",
                "Mock activity logging in Notion for MVP testing"
            ),
            "mcp_notion_pipeline_tool": create_mock_tool(
                "Mock Notion Pipeline Tool",
                "Mock pipeline management in Notion for MVP testing"
            ),
            "mcp_gmail_send_tool": create_mock_tool(
                "Mock Gmail Send Tool",
                "Mock email sending via Gmail for MVP testing"
            ),
            "mcp_gmail_search_tool": create_mock_tool(
                "Mock Gmail Search Tool",
                "Mock email searching in Gmail for MVP testing"
            ),
            "mcp_web_search_tool": create_mock_tool(
                "Mock Web Search Tool",
                "Mock web search functionality for MVP testing"
            ),
            # Security Tools
            "privategpt_security_kb_tool": create_mock_tool(
                "Mock Security Knowledge Base Tool",
                "Mock security knowledge base queries for testing"
            ),
            # n8n Integration Tools
            "n8n_trigger_workflow_tool": create_mock_tool(
                "Mock n8n Trigger Workflow Tool",
                "Mock n8n workflow triggering for testing"
            ),
            "n8n_list_workflows_tool": create_mock_tool(
                "Mock n8n List Workflows Tool",
                "Mock n8n workflow listing for testing"
            ),
            "n8n_sales_automation_tool": create_mock_tool(
                "Mock n8n Sales Automation Tool",
                "Mock sales automation via n8n for testing"
            ),
            "n8n_marketing_automation_tool": create_mock_tool(
                "Mock n8n Marketing Automation Tool",
                "Mock marketing automation via n8n for testing"
            ),
            "n8n_execute_workflow_tool": create_mock_tool(
                "Mock n8n Execute Workflow Tool",
                "Mock synchronous n8n workflow execution for testing"
            ),
        }

        return mock_tools.get(tool_name)
    
    # Try to use the real tools first
    try:
        tools_map = {
            "private_gpt_sales_full_kb_tool": PrivateGPTSalesFullKbTool(),
            "private_gpt_outbound_sales_playbook_tool": PrivateGPTOutboundSalesPlaybookTool(),
            "private_gpt_inbound_sales_playbook_tool": PrivateGPTInboundSalesPlaybookTool(),
            "private_gpt_sales_icp_tool": PrivateGPTSalesICPTool(),
            "private_gpt_sales_email_templates_tool": PrivateGPTSalesEmailTemplatesTool(),
            "private_gpt_sales_crm_tool": PrivateGPTSalesCRMTool(),
            "web_search_tool": WebSearchTool(),
            "email_sending_api_tool": EmailSendingApiTool(),
            "crm_api_tool": CrmApiTool(),
            "sequence_automation_tool": SequenceAutomationTool(),
            "lead_scoring_tool": LeadScoringTool(),
            # MCP-SuperAssistant tools
            "mcp_write_file": WriteFileMCPTool(),
            "mcp_read_file": ReadFileMCPTool(),
            "mcp_list_directory": ListDirectoryMCPTool(),
            "mcp_search_files": SearchFilesMCPTool(),
            "mcp_create_directory": CreateDirectoryMCPTool(),
            # Add delegation and reporting tools here when implemented
            "delegation_tool": None,  # Not yet implemented
            "reporting_tool": None,   # Not yet implemented
        }
        
        # Add new MCP tools for all departments
        new_mcp_tools = {
            # Admin Tools
            "mcp_calendar_read_tool": MCPCalendarReadTool(),
            "mcp_calendar_write_tool": MCPCalendarWriteTool(),
            "mcp_email_read_tool": MCPEmailReadTool(),
            "mcp_email_send_tool": MCPEmailSendTool(),
            "mcp_file_organization_tool": MCPFileOrganizationTool(),
            "mcp_notion_admin_docs_tool": MCPNotionAdminDocsTool(),
            "mcp_task_assignment_tool": MCPTaskAssignmentTool(),
            "privategpt_admin_kb_tool": PrivateGPTAdminKBTool(),
            "mcp_google_calendar_read_tool": MCPGoogleCalendarReadTool(),
            "mcp_google_calendar_write_tool": MCPGoogleCalendarWriteTool(),
            "mcp_travel_booking_tool": MCPTravelBookingTool(),
            "mcp_task_delegation_tool": MCPTaskDelegationTool(),
            "mcp_vendor_directory_tool": MCPVendorDirectoryTool(),
            "mcp_meeting_room_booking_tool": MCPMeetingRoomBookingTool(),
            "mcp_availability_checker_tool": MCPAvailabilityCheckerTool(),
            "mcp_calendar_conflict_resolver_tool": MCPCalendarConflictResolverTool(),
            
            # Marketing Tools
            "mcp_content_storage_tool": MCPContentStorageTool(),
            "mcp_notion_content_docs_tool": MCPNotionContentDocsTool(),
            "mcp_analytics_api_tool": MCPAnalyticsApiTool(),
            "privategpt_marketing_kb_tool": PrivateGPTMarketingKBTool(),
            "mcp_content_calendar_tool": MCPContentCalendarTool(),
            "mcp_seo_analysis_tool": MCPSEOAnalysisTool(),
            "mcp_video_project_file_tool": MCPVideoProjectFileTool(),
            "mcp_video_metadata_tool": MCPVideoMetadataTool(),
            "mcp_social_media_publishing_tool": MCPSocialMediaPublishingTool(),
            "mcp_asset_library_tool": MCPAssetLibraryTool(),
            "privategpt_marketing_trends_tool": PrivateGPTMarketingTrendsTool(),
            "mcp_web_search_tool": MCPWebSearchTool(),
            "mcp_idea_logging_tool": MCPIdeaLoggingTool(),
            "mcp_campaign_docs_tool": MCPCampaignDocsTool(),
            "mcp_keyword_research_tool": MCPKeywordResearchTool(),
            
            # Engineering Tools
            "mcp_code_repository_tool": MCPCodeRepositoryTool(),
            "mcp_ci_cd_trigger_tool": MCPCICDTriggerTool(),
            "mcp_bug_tracker_tool": MCPBugTrackerTool(),
            "mcp_project_management_api_tool": MCPProjectManagementApiTool(),
            "mcp_documentation_reader_tool": MCPDocumentationReaderTool(),
            "privategpt_product_kb_tool": PrivateGPTProductKBTool(),
            
            # Finance Tools
            "mcp_accounting_software_api_tool": MCPAccountingSoftwareApiTool(),
            "mcp_financial_report_writer_tool": MCPFinancialReportWriterTool(),
            "privategpt_back_office_kb_tool": PrivateGPTBackOfficeKBTool(),
            "mcp_payroll_management_tool": MCPPayrollManagementTool(),
            "mcp_invoice_generator_tool": MCPInvoiceGeneratorTool(),
            "mcp_expense_tracking_tool": MCPExpenseTrackingTool(),
            
            # Sales Tools (MVP Use Cases)
            "mcp_notion_crm_tool": MCPNotionCRMTool(),
            "mcp_notion_query_db_tool": MCPNotionQueryDBTool(),
            "mcp_notion_create_contact_tool": MCPNotionCreateContactTool(),
            "mcp_notion_update_contact_tool": MCPNotionUpdateContactTool(),
            "mcp_notion_log_activity_tool": MCPNotionLogActivityTool(),
            "mcp_notion_pipeline_tool": MCPNotionPipelineTool(),
            "mcp_gmail_send_tool": MCPGmailSendTool(),
            "mcp_gmail_search_tool": MCPGmailSearchTool(),
            "mcp_web_search_tool": MCPWebSearchTool(),
            
            # Customer Tools
            "mcp_crm_api_tool": MCPCRMApiTool(),
            "mcp_support_ticketing_api_tool": MCPSupportTicketingApiTool(),
            "mcp_report_writer_tool": MCPReportWriterTool(),
            "mcp_community_platform_tool": MCPCommunityPlatformTool(),
            "privategpt_customer_kb_tool": PrivateGPTCustomerKBTool(),
            
            # Security Tools
            "privategpt_security_kb_tool": PrivateGPTSecurityKBTool(),
            
            # New Direct RAG Knowledge Base Tools
            "admin_kb_tool": AdminKBTool(),
            "marketing_kb_tool": MarketingKBTool(),
            "product_kb_tool": ProductKBTool(),
            "back_office_kb_tool": BackOfficeKBTool(),
            "customer_kb_tool": CustomerKBTool(),
            "sales_kb_tool": SalesKBTool(),
            "security_kb_tool": SecurityKBTool(),

            # n8n Integration Tools (connects to n8n Instance-level MCP)
            "n8n_trigger_workflow_tool": N8NTriggerWorkflowTool(),
            "n8n_list_workflows_tool": N8NListWorkflowsTool(),
            "n8n_get_workflow_details_tool": N8NGetWorkflowDetailsTool(),
            "n8n_sales_automation_tool": N8NSalesAutomationTool(),
            "n8n_marketing_automation_tool": N8NMarketingAutomationTool(),
            "n8n_execute_workflow_tool": N8NExecuteWorkflowTool(),
        }

        tools_map.update(new_mcp_tools)
        
        tool = tools_map.get(tool_name)
        if tool is not None:
            return tool
    except Exception as e:
        print(f"Error creating real tool {tool_name}: {e}, falling back to mock")
    
    # If we couldn't create the real tool, fall back to mock
    return create_mock_tool(
        tool_name.replace("_", " ").title(),
        f"Tool for {tool_name.replace('_', ' ')}"
    )
