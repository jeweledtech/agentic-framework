"""
A lightweight client for interacting with privateGPT via its REST API.
This eliminates the need to install all of privateGPT's dependencies directly.
"""

import os
import requests
import logging
from typing import Dict, Any, Optional, List, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class PrivateGptClient:
    """A client for interacting with the privateGPT API."""
    
    def __init__(self, host: Optional[str] = None, collection_name: Optional[str] = None):
        """Initialize the privateGPT client.
        
        Args:
            host: The privateGPT host URL. If None, reads from PRIVATE_GPT_HOST env var.
            collection_name: The collection name to use. If None, reads from PRIVATE_GPT_COLLECTION_NAME env var.
        """
        self.host = host or os.getenv("PRIVATE_GPT_HOST", "http://localhost:8001")
        self.collection_name = collection_name or os.getenv("PRIVATE_GPT_COLLECTION_NAME", "documents")
        
        # Strip trailing slash if present
        if self.host.endswith("/"):
            self.host = self.host[:-1]
            
        logger.info(f"Initialized privateGPT client with host: {self.host}, collection: {self.collection_name}")
    
    def health_check(self) -> bool:
        """Check if privateGPT server is running.
        
        Returns:
            True if the server is running, False otherwise.
        """
        try:
            response = requests.get(f"{self.host}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error checking privateGPT health: {e}")
            return False
    
    def chat_completion(
        self, 
        prompt: str, 
        use_context: bool = True,
        collection_name: Optional[str] = None,
        include_sources: bool = False
    ) -> Dict[str, Any]:
        """Send a chat completion request to privateGPT.
        
        Args:
            prompt: The prompt to send.
            use_context: Whether to use context from the knowledge base.
            collection_name: Override the default collection name.
            include_sources: Whether to include sources in the response.
            
        Returns:
            The response from privateGPT.
        """
        if not self.health_check():
            logger.error("privateGPT server is not running")
            return {"error": "privateGPT server is not running"}
        
        # Set up the API endpoint
        api_url = f"{self.host}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        
        # Prepare the context filter
        collection = collection_name or self.collection_name
        context_filter = {
            "docs_ids": None,
            "collection_name": collection
        }
        
        # Prepare the payload for privateGPT API
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "use_context": use_context,
            "context_filter": context_filter,
            "include_sources": include_sources,
        }
        
        try:
            # Send the request
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending request to privateGPT: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error querying privateGPT: {e}")
            return {"error": str(e)}
    
    def get_response_text(self, response: Dict[str, Any]) -> str:
        """Extract the response text from a privateGPT response.
        
        Args:
            response: The response from privateGPT.
            
        Returns:
            The extracted text.
        """
        if "error" in response:
            return f"Error: {response['error']}"
        
        try:
            # Extract content from the choices
            if response.get("choices") and len(response["choices"]) > 0:
                choice = response["choices"][0]
                if isinstance(choice, dict) and "message" in choice:
                    content = choice["message"].get("content", "")
                    return content.strip() if content else "No content in response from privateGPT."
            
            # Try alternate response formats
            if response.get("content"):
                return response["content"].strip()
                
            return "Empty or unexpected response from privateGPT."
        except Exception as e:
            logger.error(f"Error parsing privateGPT response: {e}")
            return f"Error parsing privateGPT response: {e}"
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the privateGPT database.
        
        Returns:
            A list of document metadata.
        """
        if not self.health_check():
            logger.error("privateGPT server is not running")
            return []
        
        api_url = f"{self.host}/v1/ingest/list"
        payload = {"collection_name": self.collection_name}
        logger.info(f"Attempting to list documents from collection: {self.collection_name} at {api_url} via POST")
        
        try:
            response = requests.post(api_url, json=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
            documents_list = data.get('data', [])
            logger.info(f"Successfully listed {len(documents_list)} documents from privateGPT.")
            return documents_list
        except requests.exceptions.RequestException as e:
            logger.error(f"Error listing documents: {e}")
            # Try GET as fallback
            try:
                logger.info("Trying GET request as fallback...")
                response = requests.get(f"{self.host}/v1/ingest/list", timeout=20)
                response.raise_for_status()
                data = response.json()
                documents_list = data.get('data', [])
                logger.info(f"Successfully listed {len(documents_list)} documents from privateGPT using GET fallback.")
                return documents_list
            except Exception as fallback_e:
                logger.error(f"GET fallback also failed: {fallback_e}")
                return []
        except Exception as e:
            logger.error(f"Unexpected error listing documents: {e}")
            return []
    
    def query(self, query: str, collection_name: Optional[str] = None) -> str:
        """Query the privateGPT knowledge base and return text response.
        
        Args:
            query: The query to send.
            collection_name: Override the default collection name.
            
        Returns:
            The text response.
        """
        response = self.chat_completion(
            prompt=query, 
            use_context=True,
            collection_name=collection_name,
            include_sources=False
        )
        return self.get_response_text(response)
    
    def query_with_sources(self, query: str, collection_name: Optional[str] = None) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
        """Query the privateGPT knowledge base and return text with sources.
        
        Args:
            query: The query to send.
            collection_name: Override the default collection name.
            
        Returns:
            Dict with 'response' and 'sources' keys.
        """
        response = self.chat_completion(
            prompt=query, 
            use_context=True,
            collection_name=collection_name,
            include_sources=True
        )
        
        result = {
            "response": self.get_response_text(response),
            "sources": []
        }
        
        # Extract sources if available
        try:
            if response.get("choices") and len(response["choices"]) > 0:
                message = response["choices"][0].get("message", {})
                if "context" in message:
                    result["sources"] = message["context"].get("sources", [])
        except Exception as e:
            logger.error(f"Error extracting sources: {e}")
        
        return result


# Create a default client instance
privategpt_client = PrivateGptClient()

def get_privategpt_client() -> PrivateGptClient:
    """Get the singleton privateGPT client instance."""
    return privategpt_client