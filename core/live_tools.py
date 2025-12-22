"""
Enhanced Live Tools for Phase 5: Advanced Capabilities Integration

These tools integrate with MCP-SuperAssistant for live web research, browser automation, 
autonomous coding, and voice services. They leverage the enhanced LLM singleton for 
intelligent model routing (llama3:8b for general tasks, codellama:34b for coding).
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List, Union, AsyncGenerator
from datetime import datetime
import asyncio
import aiohttp

# Configure logging
logger = logging.getLogger(__name__)

# Check if CrewAI is available
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

# Import enhanced LLM singleton for intelligent model routing
from core.llm_singleton import get_singleton_llm

class StreamingLiveTool(BaseTool):
    """Enhanced base class for live tools with streaming support"""
    
    def __init__(self, mcp_url: str = None):
        super().__init__()
        self.mcp_url = mcp_url or os.getenv("MCP_URL", "http://localhost:8002")
        self.streaming_enabled = True
    
    async def stream_operation(self, endpoint: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream operation progress from MCP-SuperAssistant SSE endpoints"""
        try:
            stream_url = f"{self.mcp_url}/stream/{endpoint}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(stream_url, params=kwargs) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line = line.decode('utf-8').strip()
                            if line.startswith('data: '):
                                data = line[6:]  # Remove 'data: ' prefix
                                try:
                                    # Parse JSON data
                                    parsed_data = json.loads(data)
                                    yield json.dumps(parsed_data)
                                except json.JSONDecodeError:
                                    # Skip malformed JSON
                                    continue
                    else:
                        error_data = {
                            "type": "error",
                            "message": f"Streaming failed with status {response.status}",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        yield json.dumps(error_data)
        
        except Exception as e:
            error_data = {
                "type": "error", 
                "message": f"Streaming error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
            yield json.dumps(error_data)
    
    def supports_streaming(self) -> bool:
        """Check if this tool supports streaming operations"""
        return self.streaming_enabled

class WebSearchLiveTool(BaseTool):
    """Live web search tool via MCP-SuperAssistant with llama3:8b analysis"""
    
    name: str = "Web Search Live Tool"
    description: str = (
        "Performs live web search via AgenticSeek integration through MCP-SuperAssistant. "
        "Uses llama3:8b model for summarizing and analyzing search results. "
        "Input: search query string. Returns: analyzed search results with insights."
    )
    
    def __init__(self, mcp_url: str = None):
        super().__init__()
        if CREWAI_AVAILABLE:
            # Store as instance variables for CrewAI compatibility
            object.__setattr__(self, 'mcp_url', mcp_url or os.getenv("MCP_URL", "http://localhost:8002"))
            object.__setattr__(self, 'analysis_llm', get_singleton_llm(task_type='general'))
        else:
            self.mcp_url = mcp_url or os.getenv("MCP_URL", "http://localhost:8002")
            self.analysis_llm = get_singleton_llm(task_type='general')
        
    def _run(self, query: str, num_results: int = 10, site_filter: str = None) -> str:
        """Execute live web search and analyze results"""
        try:
            # Call MCP-SuperAssistant web search endpoint
            search_url = f"{self.mcp_url}/web-research/search"
            payload = {
                "query": query,
                "num_results": num_results,
                "site_filter": site_filter,
                "search_type": "web"
            }
            
            response = requests.post(search_url, json=payload, timeout=30)
            response.raise_for_status()
            search_data = response.json()
            
            # Extract search results
            results = search_data.get("data", {}).get("results", [])
            if not results:
                return f"No search results found for query: {query}"
            
            # Format results for LLM analysis
            formatted_results = self._format_search_results(results, query)
            
            # Use llama3:8b to analyze and summarize results
            analysis_prompt = f"""
            Analyze these web search results for the query: "{query}"
            
            Search Results:
            {formatted_results}
            
            Provide a comprehensive analysis including:
            1. Key insights and trends
            2. Most relevant findings
            3. Strategic implications
            4. Recommended next steps
            
            Format as a professional business analysis.
            """
            
            try:
                # Use the enhanced LLM for analysis
                analysis = self.analysis_llm.invoke(analysis_prompt)
                
                return f"""
## Web Search Analysis for: {query}

### Search Results Summary
Found {len(results)} results from live web search

### AI Analysis (Powered by llama3:8b)
{analysis}

### Raw Search Data
{self._format_raw_results(results[:5])}  # Top 5 results

Search completed at: {datetime.now().isoformat()}
Data source: {'Live AgenticSeek' if not search_data.get('mock') else 'Mock Data'}
                """
                
            except Exception as llm_error:
                logger.warning(f"LLM analysis failed: {llm_error}")
                # Fallback to basic formatting
                return self._format_basic_results(results, query)
                
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return f"Web search failed: {str(e)}. Please check MCP-SuperAssistant service."
    
    def _format_search_results(self, results: List[Dict], query: str) -> str:
        """Format search results for LLM analysis"""
        formatted = []
        for i, result in enumerate(results[:10], 1):
            formatted.append(f"""
Result {i}:
Title: {result.get('title', 'N/A')}
Source: {result.get('source', 'N/A')}
Date: {result.get('date', 'N/A')}
Snippet: {result.get('snippet', 'N/A')}
Relevance: {result.get('relevance_score', 'N/A')}
URL: {result.get('url', 'N/A')}
            """)
        return "\n".join(formatted)
    
    def _format_raw_results(self, results: List[Dict]) -> str:
        """Format raw results for reference"""
        formatted = []
        for result in results:
            formatted.append(f"• {result.get('title', 'N/A')} - {result.get('source', 'N/A')}")
        return "\n".join(formatted)
    
    def _format_basic_results(self, results: List[Dict], query: str) -> str:
        """Basic result formatting when LLM analysis fails"""
        formatted = [f"Web Search Results for: {query}\n"]
        for i, result in enumerate(results[:5], 1):
            formatted.append(f"{i}. {result.get('title', 'N/A')}")
            formatted.append(f"   Source: {result.get('source', 'N/A')}")
            formatted.append(f"   {result.get('snippet', 'N/A')}\n")
        return "\n".join(formatted)


class WebResearchLiveTool(StreamingLiveTool):
    """Live web research tool for comprehensive analysis via MCP-SuperAssistant with streaming support"""
    
    name: str = "Web Research Live Tool (Streaming)"
    description: str = (
        "Performs comprehensive web research and analysis via AgenticSeek integration. "
        "Uses llama3:8b model for deep analysis and strategic insights. "
        "Supports real-time streaming of research progress via @mcp/web_research/stream. "
        "Input: research topic. Returns: comprehensive research report with analysis."
    )
    
    def __init__(self, mcp_url: str = None):
        super().__init__()
        if CREWAI_AVAILABLE:
            object.__setattr__(self, 'mcp_url', mcp_url or os.getenv("MCP_URL", "http://localhost:8002"))
            object.__setattr__(self, 'analysis_llm', get_singleton_llm(task_type='general'))
        else:
            self.mcp_url = mcp_url or os.getenv("MCP_URL", "http://localhost:8002")
            self.analysis_llm = get_singleton_llm(task_type='general')
    
    def _run(self, topic: str, depth: str = "standard", sources: List[str] = None) -> str:
        """Execute comprehensive web research"""
        try:
            if sources is None:
                sources = ["web", "academic"]
            
            # Call MCP-SuperAssistant research endpoint
            research_url = f"{self.mcp_url}/web-research/research"
            payload = {
                "topic": topic,
                "depth": depth,
                "sources": sources,
                "format_type": "comprehensive"
            }
            
            response = requests.post(research_url, json=payload, timeout=60)
            response.raise_for_status()
            research_data = response.json()
            
            # Extract research findings
            data = research_data.get("data", {})
            
            # Enhanced analysis using llama3:8b
            analysis_prompt = f"""
            Provide executive-level strategic analysis of this research on: "{topic}"
            
            Research Summary: {data.get('summary', 'N/A')}
            
            Key Findings:
            {chr(10).join(f'- {finding}' for finding in data.get('key_findings', []))}
            
            Sources Analyzed:
            {chr(10).join(f'- {source.get("title", "N/A")} ({source.get("credibility", "N/A")})' for source in data.get('sources', []))}
            
            Provide:
            1. Executive Summary (3 key insights)
            2. Strategic Implications for business
            3. Market opportunities identified
            4. Risk assessment
            5. Actionable recommendations
            
            Format as professional strategic intelligence report.
            """
            
            try:
                strategic_analysis = self.analysis_llm.invoke(analysis_prompt)
                
                return f"""
# Strategic Research Intelligence: {topic}

## Executive Analysis (Powered by llama3:8b)
{strategic_analysis}

## Research Methodology
- **Depth**: {depth}
- **Sources**: {', '.join(sources)}
- **Research Completed**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **Data Source**: {'Live AgenticSeek' if not research_data.get('mock') else 'Mock Research Data'}

## Source References
{chr(10).join(f'• {source.get("title", "N/A")} - {source.get("credibility", "N/A")} credibility' for source in data.get('sources', []))}

## Next Steps
{chr(10).join(f'• {rec}' for rec in data.get('recommendations', []))}
                """
                
            except Exception as llm_error:
                logger.warning(f"Strategic analysis failed: {llm_error}")
                return self._format_basic_research(data, topic)
                
        except Exception as e:
            logger.error(f"Web research failed: {e}")
            return f"Web research failed: {str(e)}. Please check MCP-SuperAssistant service."
    
    def _format_basic_research(self, data: Dict, topic: str) -> str:
        """Basic research formatting when LLM analysis fails"""
        return f"""
Research Report: {topic}

Summary: {data.get('summary', 'N/A')}

Key Findings:
{chr(10).join(f'• {finding}' for finding in data.get('key_findings', []))}

Recommendations:
{chr(10).join(f'• {rec}' for rec in data.get('recommendations', []))}
        """
    
    async def stream_research(self, topic: str, depth: str = "standard") -> AsyncGenerator[str, None]:
        """Stream research operation with real-time progress updates"""
        async for progress in self.stream_operation("web-research", topic=topic, depth=depth):
            yield progress
    
    def get_streaming_description(self) -> str:
        """Get description for streaming capabilities"""
        return (
            "Stream web research progress in real-time using: "
            "@mcp/web_research/stream or await tool.stream_research(topic, depth)"
        )


class AutonomousCodingLiveTool(StreamingLiveTool):
    """Live autonomous coding tool via MCP-SuperAssistant with codellama:34b routing and streaming support"""
    
    name: str = "Autonomous Coding Live Tool (Streaming)"
    description: str = (
        "Generates, reviews, and optimizes code via autonomous coding service. "
        "Routes requests through codellama:34b model for superior code quality. "
        "Supports real-time streaming of code generation progress via @mcp/autonomous_coding/stream. "
        "Input: task description, language, requirements. Returns: high-quality generated code."
    )
    
    def __init__(self, mcp_url: str = None):
        super().__init__()
        if CREWAI_AVAILABLE:
            object.__setattr__(self, 'mcp_url', mcp_url or os.getenv("MCP_URL", "http://localhost:8002"))
            object.__setattr__(self, 'coding_llm', get_singleton_llm(task_type='coding'))
        else:
            self.mcp_url = mcp_url or os.getenv("MCP_URL", "http://localhost:8002")
            self.coding_llm = get_singleton_llm(task_type='coding')
        
    def _run(self, task_description: str, language: str = "python", 
             framework: str = None, requirements: List[str] = None) -> str:
        """Execute autonomous code generation"""
        try:
            if requirements is None:
                requirements = []
            
            # Call MCP-SuperAssistant coding endpoint
            coding_url = f"{self.mcp_url}/autonomous-coding/generate"
            payload = {
                "task_description": task_description,
                "language": language,
                "framework": framework,
                "requirements": requirements,
                "style": "clean"
            }
            
            response = requests.post(coding_url, json=payload, timeout=120)
            response.raise_for_status()
            coding_data = response.json()
            
            # Extract generated code
            data = coding_data.get("data", {})
            generated_code = data.get("generated_code", "")
            
            # Enhanced code review and optimization using codellama:34b
            review_prompt = f"""
            Review and enhance this generated code for: "{task_description}"
            
            Generated Code:
            ```{language}
            {generated_code}
            ```
            
            Language: {language}
            Framework: {framework or 'None'}
            Requirements: {', '.join(requirements) if requirements else 'None'}
            
            Provide:
            1. Code quality assessment
            2. Potential improvements
            3. Security considerations
            4. Performance optimizations
            5. Best practices compliance
            6. Enhanced version if needed
            
            Format as professional code review with improved code if applicable.
            """
            
            try:
                code_review = self.coding_llm.invoke(review_prompt)
                
                return f"""
# Autonomous Code Generation: {task_description}

## Generated Code ({language})
```{language}
{generated_code}
```

## Expert Code Review (Powered by codellama:34b)
{code_review}

## Code Metadata
- **Language**: {language}
- **Framework**: {framework or 'None'}
- **Requirements**: {', '.join(requirements) if requirements else 'None'}
- **Estimated Lines**: {data.get('estimated_lines', 'N/A')}
- **Complexity**: {data.get('complexity', 'N/A')}
- **Dependencies**: {', '.join(data.get('dependencies', [])) if data.get('dependencies') else 'None'}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **Service**: {'Live Autonomous Coding' if not coding_data.get('mock') else 'Mock Code Generation'}

## Implementation Notes
{data.get('explanation', 'Code generated according to specifications.')}
                """
                
            except Exception as llm_error:
                logger.warning(f"Code review failed: {llm_error}")
                return self._format_basic_code(data, task_description, language)
                
        except Exception as e:
            logger.error(f"Autonomous coding failed: {e}")
            return f"Autonomous coding failed: {str(e)}. Please check MCP-SuperAssistant service."
    
    def _format_basic_code(self, data: Dict, task: str, language: str) -> str:
        """Basic code formatting when LLM review fails"""
        return f"""
Code Generation: {task}

Language: {language}

Generated Code:
```{language}
{data.get('generated_code', 'Code generation failed')}
```

Explanation: {data.get('explanation', 'N/A')}
Dependencies: {', '.join(data.get('dependencies', [])) if data.get('dependencies') else 'None'}
        """
    
    async def stream_code_generation(self, task_description: str, language: str = "python") -> AsyncGenerator[str, None]:
        """Stream code generation operation with real-time progress updates"""
        async for progress in self.stream_operation("code-generation", task_description=task_description, language=language):
            yield progress
    
    def get_streaming_description(self) -> str:
        """Get description for streaming capabilities"""
        return (
            "Stream code generation progress in real-time using: "
            "@mcp/autonomous_coding/stream or await tool.stream_code_generation(task, language)"
        )


class CodeReviewLiveTool(BaseTool):
    """Live code review tool with expert analysis via codellama:34b"""
    
    name: str = "Code Review Live Tool"
    description: str = (
        "Performs comprehensive code review using autonomous coding service. "
        "Leverages codellama:34b for expert-level code analysis and recommendations. "
        "Input: code to review, language. Returns: detailed code review with improvements."
    )
    
    def __init__(self, mcp_url: str = None):
        super().__init__()
        if CREWAI_AVAILABLE:
            object.__setattr__(self, 'mcp_url', mcp_url or os.getenv("MCP_URL", "http://localhost:8002"))
            object.__setattr__(self, 'coding_llm', get_singleton_llm(task_type='coding'))
        else:
            self.mcp_url = mcp_url or os.getenv("MCP_URL", "http://localhost:8002")
            self.coding_llm = get_singleton_llm(task_type='coding')
    
    def _run(self, code: str, language: str = "python", 
             focus_areas: List[str] = None) -> str:
        """Execute comprehensive code review"""
        try:
            if focus_areas is None:
                focus_areas = ["performance", "security", "maintainability"]
            
            # Call MCP-SuperAssistant code review endpoint
            review_url = f"{self.mcp_url}/autonomous-coding/review"
            payload = {
                "code": code,
                "language": language,
                "review_type": "comprehensive",
                "focus_areas": focus_areas
            }
            
            response = requests.post(review_url, json=payload, timeout=60)
            response.raise_for_status()
            review_data = response.json()
            
            # Extract review results
            data = review_data.get("data", {})
            
            # Enhanced analysis using codellama:34b
            enhancement_prompt = f"""
            Provide expert-level code review analysis for this {language} code:
            
            Code Quality Score: {data.get('overall_score', 'N/A')}/10
            
            Issues Found:
            {chr(10).join(f'- {issue.get("message", "N/A")} (Line {issue.get("line", "N/A")})' for issue in data.get('issues_found', []))}
            
            Code Strengths:
            {chr(10).join(f'- {strength}' for strength in data.get('strengths', []))}
            
            Provide:
            1. Executive summary of code quality
            2. Priority improvements ranked by impact
            3. Security analysis
            4. Performance optimization opportunities
            5. Refactored code examples for key issues
            
            Format as professional engineering review.
            """
            
            try:
                expert_analysis = self.coding_llm.invoke(enhancement_prompt)
                
                return f"""
# Expert Code Review Analysis

## Code Quality Assessment
- **Overall Score**: {data.get('overall_score', 'N/A')}/10
- **Quality Level**: {data.get('code_quality', 'N/A')}
- **Language**: {language}
- **Focus Areas**: {', '.join(focus_areas)}

## Expert Analysis (Powered by codellama:34b)
{expert_analysis}

## Detailed Findings

### Issues Identified
{chr(10).join(f'**{issue.get("severity", "Unknown").title()} - Line {issue.get("line", "N/A")}**: {issue.get("message", "N/A")}' for issue in data.get('issues_found', []))}

### Code Strengths
{chr(10).join(f'• {strength}' for strength in data.get('strengths', []))}

### Recommendations
{chr(10).join(f'• {rec}' for rec in data.get('recommendations', []))}

## Quality Metrics
- **Cyclomatic Complexity**: {data.get('metrics', {}).get('cyclomatic_complexity', 'N/A')}
- **Maintainability Index**: {data.get('metrics', {}).get('maintainability_index', 'N/A')}
- **Test Coverage**: {data.get('metrics', {}).get('test_coverage', 'N/A')}%

Review completed: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Service: {'Live Code Review' if not review_data.get('mock') else 'Mock Code Review'}
                """
                
            except Exception as llm_error:
                logger.warning(f"Expert analysis failed: {llm_error}")
                return self._format_basic_review(data, language)
                
        except Exception as e:
            logger.error(f"Code review failed: {e}")
            return f"Code review failed: {str(e)}. Please check MCP-SuperAssistant service."
    
    def _format_basic_review(self, data: Dict, language: str) -> str:
        """Basic review formatting when LLM analysis fails"""
        return f"""
Code Review Results ({language})

Overall Score: {data.get('overall_score', 'N/A')}/10

Issues Found:
{chr(10).join(f'• {issue.get("message", "N/A")}' for issue in data.get('issues_found', []))}

Recommendations:
{chr(10).join(f'• {rec}' for rec in data.get('recommendations', []))}
        """


class VoiceInteractionLiveTool(StreamingLiveTool):
    """Live voice interaction tool for STT/TTS via MCP-SuperAssistant with streaming support"""
    
    name: str = "Voice Interaction Live Tool (Streaming)"
    description: str = (
        "Handles speech-to-text and text-to-speech via voice services integration. "
        "Supports real-time voice interactions and voice cloning capabilities with streaming progress. "
        "Streaming available via @mcp/voice_services/stream for real-time audio processing feedback. "
        "Input: audio data or text. Returns: transcription or audio response."
    )
    
    def __init__(self, mcp_url: str = None):
        super().__init__()
        if CREWAI_AVAILABLE:
            object.__setattr__(self, 'mcp_url', mcp_url or os.getenv("MCP_URL", "http://localhost:8002"))
        else:
            self.mcp_url = mcp_url or os.getenv("MCP_URL", "http://localhost:8002")
    
    def _run(self, action: str, content: str, **kwargs) -> str:
        """Execute voice interaction (STT/TTS)"""
        try:
            if action == "speech_to_text":
                return self._speech_to_text(content, **kwargs)
            elif action == "text_to_speech":
                return self._text_to_speech(content, **kwargs)
            elif action == "voice_clone":
                return self._voice_clone(content, **kwargs)
            else:
                return f"Unknown voice action: {action}. Supported actions: speech_to_text, text_to_speech, voice_clone"
                
        except Exception as e:
            logger.error(f"Voice interaction failed: {e}")
            return f"Voice interaction failed: {str(e)}. Please check MCP-SuperAssistant service."
    
    def _speech_to_text(self, audio_data: str, **kwargs) -> str:
        """Convert speech to text"""
        stt_url = f"{self.mcp_url}/voice/speech-to-text"
        payload = {
            "audio_data": audio_data,
            "audio_format": kwargs.get("audio_format", "wav"),
            "language": kwargs.get("language", "en-US"),
            "model": kwargs.get("model", "whisper")
        }
        
        response = requests.post(stt_url, json=payload, timeout=60)
        response.raise_for_status()
        stt_data = response.json()
        
        data = stt_data.get("data", {})
        return f"""
Speech-to-Text Result:

Transcript: {data.get('transcript', 'N/A')}
Confidence: {data.get('confidence', 'N/A')}
Language: {data.get('language', 'N/A')}
Duration: {data.get('duration', 'N/A')}s

Service: {'Live Voice Processing' if not stt_data.get('mock') else 'Mock STT'}
        """
    
    def _text_to_speech(self, text: str, **kwargs) -> str:
        """Convert text to speech"""
        tts_url = f"{self.mcp_url}/voice/text-to-speech"
        payload = {
            "text": text,
            "voice": kwargs.get("voice", "default"),
            "language": kwargs.get("language", "en-US"),
            "speed": kwargs.get("speed", 1.0),
            "format_type": kwargs.get("format", "mp3")
        }
        
        response = requests.post(tts_url, json=payload, timeout=30)
        response.raise_for_status()
        tts_data = response.json()
        
        data = tts_data.get("data", {})
        return f"""
Text-to-Speech Result:

Audio URL: {data.get('audio_url', 'N/A')}
Voice: {data.get('voice', 'N/A')}
Language: {data.get('language', 'N/A')}
Duration: {data.get('duration', 'N/A')}s
Format: {data.get('format', 'N/A')}
Size: {data.get('size_bytes', 'N/A')} bytes

Service: {'Live Voice Synthesis' if not tts_data.get('mock') else 'Mock TTS'}
        """
    
    def _voice_clone(self, text: str, **kwargs) -> str:
        """Clone voice for text"""
        clone_url = f"{self.mcp_url}/voice/clone"
        payload = {
            "text": text,
            "reference_audio": kwargs.get("reference_audio"),
            "target_voice_id": kwargs.get("target_voice_id"),
            "quality": kwargs.get("quality", "high")
        }
        
        response = requests.post(clone_url, json=payload, timeout=90)
        response.raise_for_status()
        clone_data = response.json()
        
        data = clone_data.get("data", {})
        return f"""
Voice Cloning Result:

Cloned Audio URL: {data.get('cloned_audio_url', 'N/A')}
Target Voice: {data.get('target_voice_id', 'N/A')}
Similarity Score: {data.get('similarity_score', 'N/A')}
Quality: {data.get('quality', 'N/A')}
Processing Time: {data.get('processing_time', 'N/A')}s

Voice Characteristics:
- Pitch: {data.get('voice_characteristics', {}).get('pitch', 'N/A')}
- Tone: {data.get('voice_characteristics', {}).get('tone', 'N/A')}
- Accent: {data.get('voice_characteristics', {}).get('accent', 'N/A')}

Service: {'Live Voice Cloning' if not clone_data.get('mock') else 'Mock Voice Cloning'}
        """
    
    async def stream_voice_processing(self, text: str, operation: str = "text_to_speech") -> AsyncGenerator[str, None]:
        """Stream voice processing operation with real-time progress updates"""
        async for progress in self.stream_operation("voice-processing", text=text, operation=operation):
            yield progress
    
    def get_streaming_description(self) -> str:
        """Get description for streaming capabilities"""
        return (
            "Stream voice processing progress in real-time using: "
            "@mcp/voice_services/stream or await tool.stream_voice_processing(text, operation)"
        )


# Tool registry for easy access with @-mentionable resources
LIVE_TOOLS = {
    "web_search": WebSearchLiveTool,
    "web_research": WebResearchLiveTool,
    "autonomous_coding": AutonomousCodingLiveTool,
    "code_review": CodeReviewLiveTool,
    "voice_interaction": VoiceInteractionLiveTool
}

# @-mentionable MCP resource registry
MCP_RESOURCES = {
    "@mcp/web_search": {
        "tool_class": WebSearchLiveTool,
        "description": "Live web search with llama3:8b analysis",
        "streaming": False,
        "endpoints": ["search", "trends"],
        "examples": ["@mcp/web_search(query='AI trends 2024')"]
    },
    "@mcp/web_research": {
        "tool_class": WebResearchLiveTool,
        "description": "Comprehensive web research with streaming progress",
        "streaming": True,
        "endpoints": ["research", "stream"],
        "examples": [
            "@mcp/web_research(topic='machine learning trends')",
            "@mcp/web_research/stream(topic='AI market analysis')"
        ]
    },
    "@mcp/autonomous_coding": {
        "tool_class": AutonomousCodingLiveTool,
        "description": "Code generation with codellama:34b and streaming",
        "streaming": True,
        "endpoints": ["generate", "review", "stream"],
        "examples": [
            "@mcp/autonomous_coding(task='create REST API', language='python')",
            "@mcp/autonomous_coding/stream(task='build web scraper')"
        ]
    },
    "@mcp/code_review": {
        "tool_class": CodeReviewLiveTool,
        "description": "Expert code review with codellama:34b analysis",
        "streaming": False,
        "endpoints": ["review", "analyze"],
        "examples": ["@mcp/code_review(code='def hello(): print(\"world\")', language='python')"]
    },
    "@mcp/voice_services": {
        "tool_class": VoiceInteractionLiveTool,
        "description": "Voice processing (STT/TTS) with streaming support",
        "streaming": True,
        "endpoints": ["speech_to_text", "text_to_speech", "clone", "stream"],
        "examples": [
            "@mcp/voice_services(text='Hello world', action='text_to_speech')",
            "@mcp/voice_services/stream(text='Processing audio...')"
        ]
    }
}

def get_live_tool(tool_name: str, **kwargs):
    """Get a live tool instance by name"""
    if tool_name not in LIVE_TOOLS:
        raise ValueError(f"Unknown live tool: {tool_name}. Available: {list(LIVE_TOOLS.keys())}")
    
    return LIVE_TOOLS[tool_name](**kwargs)

def get_mcp_resource(resource_name: str, **kwargs):
    """Get a tool instance by @-mentionable MCP resource name"""
    if resource_name not in MCP_RESOURCES:
        available_resources = list(MCP_RESOURCES.keys())
        raise ValueError(f"Unknown MCP resource: {resource_name}. Available: {available_resources}")
    
    tool_class = MCP_RESOURCES[resource_name]["tool_class"]
    return tool_class(**kwargs)

def list_live_tools() -> List[str]:
    """List all available live tools"""
    return list(LIVE_TOOLS.keys())

def list_mcp_resources() -> Dict[str, Dict[str, Any]]:
    """List all @-mentionable MCP resources with details"""
    return MCP_RESOURCES

def get_streaming_tools() -> List[str]:
    """Get list of tools that support streaming"""
    return [name for name, info in MCP_RESOURCES.items() if info.get("streaming", False)]

def get_resource_examples() -> Dict[str, List[str]]:
    """Get usage examples for all MCP resources"""
    return {resource: info["examples"] for resource, info in MCP_RESOURCES.items()}

def format_mcp_resources_help() -> str:
    """Format help text for @-mentionable MCP resources"""
    help_text = ["# @-Mentionable MCP Resources\n"]
    
    for resource, info in MCP_RESOURCES.items():
        help_text.append(f"## {resource}")
        help_text.append(f"**Description**: {info['description']}")
        help_text.append(f"**Streaming**: {'✅ Yes' if info['streaming'] else '❌ No'}")
        help_text.append(f"**Endpoints**: {', '.join(info['endpoints'])}")
        help_text.append("**Examples**:")
        for example in info['examples']:
            help_text.append(f"  - `{example}`")
        help_text.append("")
    
    return "\n".join(help_text)