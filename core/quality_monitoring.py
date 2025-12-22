"""
Enhanced quality monitoring and continuous improvement system
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class QualityMonitoringSystem:
    """Comprehensive quality monitoring for agentic platform"""
    
    def __init__(self):
        self.quality_metrics = {
            "agent_performance": {},
            "tool_effectiveness": {},
            "communication_quality": {},
            "business_outcome_alignment": {}
        }
        self.performance_history = []
        self.quality_thresholds = {
            "minimum_quality_score": 0.7,
            "excellent_quality_score": 0.9,
            "response_time_threshold": 300,  # 5 minutes in seconds
            "accuracy_threshold": 0.85
        }
        
    def monitor_agent_performance(self, agent_id: str, task_results: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor individual agent performance metrics"""
        
        performance_assessment = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "task_completion_rate": self._calculate_completion_rate(agent_id, task_results),
            "response_quality_score": self._assess_response_quality(task_results),
            "business_alignment_score": self._assess_business_alignment(task_results),
            "collaboration_effectiveness": self._assess_collaboration(agent_id, task_results),
            "tool_usage_efficiency": self._assess_tool_usage_efficiency(task_results),
            "improvement_opportunities": self._identify_improvements(agent_id, task_results),
            "overall_performance_score": 0.0
        }
        
        # Calculate overall performance score
        performance_assessment["overall_performance_score"] = (
            performance_assessment["task_completion_rate"] * 0.25 +
            performance_assessment["response_quality_score"] * 0.25 +
            performance_assessment["business_alignment_score"] * 0.25 +
            performance_assessment["collaboration_effectiveness"] * 0.15 +
            performance_assessment["tool_usage_efficiency"] * 0.10
        )
        
        # Store performance history
        self.performance_history.append(performance_assessment)
        
        # Update agent performance metrics
        self.quality_metrics["agent_performance"][agent_id] = performance_assessment
        
        # Generate performance alerts if needed
        alerts = self._generate_performance_alerts(performance_assessment)
        if alerts:
            performance_assessment["alerts"] = alerts
        
        return performance_assessment
    
    def monitor_tool_effectiveness(self, tool_usage_log: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Monitor tool usage effectiveness and efficiency"""
        
        tool_analysis = {}
        
        for tool_entry in tool_usage_log:
            tool_name = tool_entry.get("tool", "unknown")
            
            if tool_name not in tool_analysis:
                tool_analysis[tool_name] = {
                    "usage_count": 0,
                    "success_count": 0,
                    "total_response_time": 0,
                    "quality_scores": [],
                    "business_impact_scores": []
                }
            
            analysis_entry = tool_analysis[tool_name]
            analysis_entry["usage_count"] += 1
            
            # Extract metrics from tool entry
            if tool_entry.get("analysis", {}).get("tool_selection_appropriate", 0) > 0.8:
                analysis_entry["success_count"] += 1
            
            # Mock response time calculation
            analysis_entry["total_response_time"] += 2.5  # Mock: 2.5 seconds average
            
            # Quality scoring
            quality_score = self._calculate_tool_quality_score(tool_entry)
            analysis_entry["quality_scores"].append(quality_score)
            
            # Business impact scoring
            business_impact = self._calculate_business_impact_score(tool_entry)
            analysis_entry["business_impact_scores"].append(business_impact)
        
        # Calculate aggregate metrics for each tool
        for tool_name, data in tool_analysis.items():
            if data["usage_count"] > 0:
                data["success_rate"] = data["success_count"] / data["usage_count"]
                data["avg_response_time"] = data["total_response_time"] / data["usage_count"]
                data["avg_quality_score"] = sum(data["quality_scores"]) / len(data["quality_scores"]) if data["quality_scores"] else 0
                data["avg_business_impact"] = sum(data["business_impact_scores"]) / len(data["business_impact_scores"]) if data["business_impact_scores"] else 0
                
                # Overall tool effectiveness score
                data["effectiveness_score"] = (
                    data["success_rate"] * 0.4 +
                    data["avg_quality_score"] * 0.3 +
                    data["avg_business_impact"] * 0.3
                )
        
        # Update tool effectiveness metrics
        self.quality_metrics["tool_effectiveness"] = tool_analysis
        
        return tool_analysis
    
    def monitor_communication_quality(self, communication_log: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Monitor inter-agent communication quality"""
        
        communication_metrics = {
            "total_communications": len(communication_log),
            "average_response_time": 0,
            "escalation_rate": 0,
            "collaboration_success_rate": 0,
            "message_clarity_score": 0,
            "communication_effectiveness": 0
        }
        
        if communication_log:
            # Calculate response times
            response_times = []
            escalations = 0
            collaborations = 0
            successful_collaborations = 0
            clarity_scores = []
            
            for comm in communication_log:
                msg_type = comm.get("message_type", "")
                
                if msg_type == "ESCALATION":
                    escalations += 1
                elif msg_type == "COLLABORATION_REQUEST":
                    collaborations += 1
                    # Mock collaboration success assessment
                    if comm.get("payload", {}).get("status") == "COMPLETED":
                        successful_collaborations += 1
                
                # Mock response time (would calculate from actual timestamps)
                response_times.append(120)  # 2 minutes average
                
                # Mock clarity score assessment
                clarity_scores.append(self._assess_message_clarity(comm))
            
            # Calculate metrics
            communication_metrics["average_response_time"] = sum(response_times) / len(response_times)
            communication_metrics["escalation_rate"] = escalations / len(communication_log)
            communication_metrics["collaboration_success_rate"] = (
                successful_collaborations / collaborations if collaborations > 0 else 1.0
            )
            communication_metrics["message_clarity_score"] = (
                sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0
            )
            
            # Overall communication effectiveness
            communication_metrics["communication_effectiveness"] = (
                (1 - communication_metrics["escalation_rate"]) * 0.3 +
                communication_metrics["collaboration_success_rate"] * 0.3 +
                communication_metrics["message_clarity_score"] * 0.4
            )
        
        # Update communication quality metrics
        self.quality_metrics["communication_quality"] = communication_metrics
        
        return communication_metrics
    
    def assess_business_outcome_alignment(self, business_objectives: List[Dict[str, Any]], 
                                        agent_outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess how well agent outputs align with business objectives"""
        
        alignment_assessment = {
            "overall_alignment_score": 0.0,
            "objective_completion_rates": {},
            "value_delivery_score": 0.0,
            "strategic_impact_score": 0.0,
            "operational_efficiency_score": 0.0
        }
        
        if business_objectives and agent_outputs:
            objective_scores = []
            
            for objective in business_objectives:
                objective_id = objective.get("id", "unknown")
                target_metrics = objective.get("target_metrics", {})
                
                # Find related agent outputs
                related_outputs = [
                    output for output in agent_outputs 
                    if objective_id in output.get("related_objectives", [])
                ]
                
                # Calculate objective completion score
                completion_score = self._calculate_objective_completion(objective, related_outputs)
                objective_scores.append(completion_score)
                alignment_assessment["objective_completion_rates"][objective_id] = completion_score
            
            # Calculate overall scores
            alignment_assessment["overall_alignment_score"] = (
                sum(objective_scores) / len(objective_scores) if objective_scores else 0
            )
            
            # Mock additional scores (would be calculated from actual business metrics)
            alignment_assessment["value_delivery_score"] = 0.87
            alignment_assessment["strategic_impact_score"] = 0.82
            alignment_assessment["operational_efficiency_score"] = 0.91
        
        # Update business outcome alignment metrics
        self.quality_metrics["business_outcome_alignment"] = alignment_assessment
        
        return alignment_assessment
    
    def generate_improvement_recommendations(self) -> Dict[str, Any]:
        """Generate system-wide improvement recommendations"""
        
        recommendations = {
            "prompt_optimizations": self._analyze_prompt_effectiveness(),
            "tool_integration_improvements": self._analyze_tool_integration(),
            "agent_coordination_enhancements": self._analyze_coordination(),
            "business_alignment_adjustments": self._analyze_business_alignment(),
            "performance_optimization": self._analyze_performance_patterns(),
            "communication_improvements": self._analyze_communication_patterns()
        }
        
        # Prioritize recommendations
        recommendations["priority_actions"] = self._prioritize_recommendations(recommendations)
        
        return recommendations
    
    def generate_quality_report(self, time_period: str = "last_24_hours") -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        
        # Filter performance history by time period
        cutoff_time = self._get_cutoff_time(time_period)
        recent_performance = [
            perf for perf in self.performance_history 
            if datetime.fromisoformat(perf["timestamp"]) >= cutoff_time
        ]
        
        report = {
            "report_period": time_period,
            "report_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_agents_monitored": len(set(perf["agent_id"] for perf in recent_performance)),
                "average_performance_score": self._calculate_average_performance(recent_performance),
                "quality_alerts": self._get_active_quality_alerts(),
                "improvement_trend": self._calculate_improvement_trend(recent_performance)
            },
            "detailed_metrics": {
                "agent_performance": self.quality_metrics.get("agent_performance", {}),
                "tool_effectiveness": self.quality_metrics.get("tool_effectiveness", {}),
                "communication_quality": self.quality_metrics.get("communication_quality", {}),
                "business_alignment": self.quality_metrics.get("business_outcome_alignment", {})
            },
            "recommendations": self.generate_improvement_recommendations(),
            "quality_trends": self._analyze_quality_trends(recent_performance),
            "next_review_date": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        return report
    
    # Helper methods for quality assessment
    
    def _calculate_completion_rate(self, agent_id: str, task_results: Dict[str, Any]) -> float:
        """Calculate task completion rate for agent"""
        # Mock implementation - would track actual task completion
        return task_results.get("completion_rate", 0.95)
    
    def _assess_response_quality(self, task_results: Dict[str, Any]) -> float:
        """Assess the quality of agent responses"""
        quality_indicators = task_results.get("quality_indicators", {})
        
        # Weighted quality assessment
        relevance = quality_indicators.get("relevance", 0.8)
        accuracy = quality_indicators.get("accuracy", 0.8)
        completeness = quality_indicators.get("completeness", 0.8)
        clarity = quality_indicators.get("clarity", 0.8)
        
        return (relevance * 0.3 + accuracy * 0.3 + completeness * 0.25 + clarity * 0.15)
    
    def _assess_business_alignment(self, task_results: Dict[str, Any]) -> float:
        """Assess alignment with business objectives"""
        business_metrics = task_results.get("business_metrics", {})
        
        # Mock business alignment assessment
        strategic_value = business_metrics.get("strategic_value", 0.85)
        operational_impact = business_metrics.get("operational_impact", 0.88)
        stakeholder_satisfaction = business_metrics.get("stakeholder_satisfaction", 0.90)
        
        return (strategic_value * 0.4 + operational_impact * 0.35 + stakeholder_satisfaction * 0.25)
    
    def _assess_collaboration(self, agent_id: str, task_results: Dict[str, Any]) -> float:
        """Assess collaboration effectiveness"""
        collaboration_metrics = task_results.get("collaboration_metrics", {})
        
        # Mock collaboration assessment
        return collaboration_metrics.get("collaboration_score", 0.85)
    
    def _assess_tool_usage_efficiency(self, task_results: Dict[str, Any]) -> float:
        """Assess efficiency of tool usage"""
        tool_metrics = task_results.get("tool_metrics", {})
        
        tool_selection_accuracy = tool_metrics.get("selection_accuracy", 0.88)
        execution_efficiency = tool_metrics.get("execution_efficiency", 0.85)
        result_utilization = tool_metrics.get("result_utilization", 0.82)
        
        return (tool_selection_accuracy * 0.4 + execution_efficiency * 0.35 + result_utilization * 0.25)
    
    def _identify_improvements(self, agent_id: str, task_results: Dict[str, Any]) -> List[str]:
        """Identify improvement opportunities for agent"""
        improvements = []
        
        performance_metrics = task_results.get("performance_metrics", {})
        
        if performance_metrics.get("response_time", 300) > self.quality_thresholds["response_time_threshold"]:
            improvements.append("Optimize response time through better tool selection")
        
        if performance_metrics.get("accuracy", 0.85) < self.quality_thresholds["accuracy_threshold"]:
            improvements.append("Improve accuracy through enhanced validation processes")
        
        if task_results.get("quality_score", 0.8) < self.quality_thresholds["minimum_quality_score"]:
            improvements.append("Review and enhance prompt engineering")
        
        return improvements
    
    def _calculate_tool_quality_score(self, tool_entry: Dict[str, Any]) -> float:
        """Calculate quality score for tool usage"""
        analysis = tool_entry.get("analysis", {})
        
        appropriateness = analysis.get("tool_selection_appropriate", 0.8)
        completeness = analysis.get("parameters_complete", 0.8)
        effectiveness = analysis.get("output_effectiveness", 0.8)
        
        return (appropriateness * 0.4 + completeness * 0.3 + effectiveness * 0.3)
    
    def _calculate_business_impact_score(self, tool_entry: Dict[str, Any]) -> float:
        """Calculate business impact score for tool usage"""
        justification = tool_entry.get("justification", "")
        
        # Mock business impact assessment based on justification
        if "critical" in justification.lower():
            return 0.95
        elif "important" in justification.lower():
            return 0.85
        elif "routine" in justification.lower():
            return 0.70
        else:
            return 0.75
    
    def _assess_message_clarity(self, communication: Dict[str, Any]) -> float:
        """Assess clarity of communication message"""
        payload = communication.get("payload", {})
        
        # Mock clarity assessment
        has_clear_objective = bool(payload.get("task_description"))
        has_success_criteria = bool(payload.get("success_criteria"))
        has_timeline = bool(payload.get("deadline"))
        
        clarity_factors = [has_clear_objective, has_success_criteria, has_timeline]
        return sum(clarity_factors) / len(clarity_factors)
    
    def _calculate_objective_completion(self, objective: Dict[str, Any], 
                                      related_outputs: List[Dict[str, Any]]) -> float:
        """Calculate completion score for business objective"""
        if not related_outputs:
            return 0.0
        
        # Mock objective completion assessment
        target_value = objective.get("target_value", 100)
        achieved_value = sum(output.get("achieved_value", 0) for output in related_outputs)
        
        completion_rate = min(achieved_value / target_value, 1.0) if target_value > 0 else 0.0
        return completion_rate
    
    def _generate_performance_alerts(self, performance_assessment: Dict[str, Any]) -> List[str]:
        """Generate performance alerts based on thresholds"""
        alerts = []
        
        if performance_assessment["overall_performance_score"] < self.quality_thresholds["minimum_quality_score"]:
            alerts.append(f"ALERT: Agent {performance_assessment['agent_id']} performance below threshold")
        
        if performance_assessment["response_quality_score"] < self.quality_thresholds["minimum_quality_score"]:
            alerts.append(f"ALERT: Response quality concerns for agent {performance_assessment['agent_id']}")
        
        return alerts
    
    def _analyze_prompt_effectiveness(self) -> List[str]:
        """Analyze prompt effectiveness and suggest improvements"""
        return [
            "Consider more specific business context in prompts",
            "Add clearer success criteria definitions",
            "Enhance tool selection guidance in prompts"
        ]
    
    def _analyze_tool_integration(self) -> List[str]:
        """Analyze tool integration and suggest improvements"""
        return [
            "Implement better error handling for tool failures",
            "Add more comprehensive tool validation",
            "Enhance tool result interpretation capabilities"
        ]
    
    def _analyze_coordination(self) -> List[str]:
        """Analyze agent coordination and suggest improvements"""
        return [
            "Improve handoff processes between agents",
            "Enhance collaboration communication protocols",
            "Implement better dependency management"
        ]
    
    def _analyze_business_alignment(self) -> List[str]:
        """Analyze business alignment and suggest improvements"""
        return [
            "Strengthen connection between agent outputs and business KPIs",
            "Improve tracking of business objective completion",
            "Enhance stakeholder feedback integration"
        ]
    
    def _analyze_performance_patterns(self) -> List[str]:
        """Analyze performance patterns and suggest improvements"""
        return [
            "Optimize resource allocation during peak usage periods",
            "Implement predictive performance monitoring",
            "Enhance agent learning from performance feedback"
        ]
    
    def _analyze_communication_patterns(self) -> List[str]:
        """Analyze communication patterns and suggest improvements"""
        return [
            "Standardize communication templates across all agents",
            "Implement automated escalation triggers",
            "Enhance cross-departmental communication protocols"
        ]
    
    def _prioritize_recommendations(self, recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize improvement recommendations"""
        return [
            {"priority": "HIGH", "area": "Tool Integration", "action": "Implement better error handling"},
            {"priority": "MEDIUM", "area": "Communication", "action": "Standardize templates"},
            {"priority": "LOW", "area": "Performance", "action": "Optimize resource allocation"}
        ]
    
    def _get_cutoff_time(self, time_period: str) -> datetime:
        """Get cutoff time for filtering performance data"""
        now = datetime.now()
        if time_period == "last_24_hours":
            return now - timedelta(hours=24)
        elif time_period == "last_week":
            return now - timedelta(weeks=1)
        elif time_period == "last_month":
            return now - timedelta(days=30)
        else:
            return now - timedelta(hours=24)  # Default
    
    def _calculate_average_performance(self, performance_data: List[Dict[str, Any]]) -> float:
        """Calculate average performance score"""
        if not performance_data:
            return 0.0
        
        scores = [perf.get("overall_performance_score", 0) for perf in performance_data]
        return sum(scores) / len(scores)
    
    def _get_active_quality_alerts(self) -> List[str]:
        """Get currently active quality alerts"""
        alerts = []
        for agent_perf in self.quality_metrics.get("agent_performance", {}).values():
            alerts.extend(agent_perf.get("alerts", []))
        return alerts
    
    def _calculate_improvement_trend(self, performance_data: List[Dict[str, Any]]) -> str:
        """Calculate improvement trend"""
        if len(performance_data) < 2:
            return "INSUFFICIENT_DATA"
        
        # Sort by timestamp and compare recent vs older performance
        sorted_data = sorted(performance_data, key=lambda x: x["timestamp"])
        recent_avg = sum(perf["overall_performance_score"] for perf in sorted_data[-5:]) / min(5, len(sorted_data))
        older_avg = sum(perf["overall_performance_score"] for perf in sorted_data[:-5]) / max(1, len(sorted_data) - 5)
        
        if recent_avg > older_avg + 0.05:
            return "IMPROVING"
        elif recent_avg < older_avg - 0.05:
            return "DECLINING"
        else:
            return "STABLE"
    
    def _analyze_quality_trends(self, performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quality trends over time"""
        return {
            "performance_trend": self._calculate_improvement_trend(performance_data),
            "quality_stability": "STABLE",  # Mock
            "prediction": "Performance expected to improve with recent optimizations"
        }