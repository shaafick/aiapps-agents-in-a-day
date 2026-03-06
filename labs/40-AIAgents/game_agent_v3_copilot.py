import os
import asyncio
from dotenv import load_dotenv
from copilot import CopilotClient

load_dotenv()


class GameAgent:
    """GitHub Copilot SDK with BYOK for RPS Tournament
    
    This implementation uses the actual GitHub Copilot SDK with BYOK (Bring Your Own Key)
    from Microsoft Foundry. Uses API keys for authentication, not Azure CLI.
    
    Package: pip install copilot
    BYOK: Uses your Microsoft Foundry API keys directly
    """
    
    def __init__(self, player_name=None, model=None):
        """Initialize GitHub Copilot SDK with BYOK
        
        Args:
            player_name: Name of the player/agent
            model: Model deployment name (e.g., 'gpt-4o')
        """
        self.player_name = player_name or os.getenv('DEV_Name', 'default-player')
        self.model = model or os.getenv('AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME', 'gpt-4o')
        foundry_endpoint = os.getenv('AZURE_FOUNDRY_PROJECT_ENDPOINT')
        self.api_key = os.getenv('AZURE_FOUNDRY_API_KEY')
        
        if not foundry_endpoint:
            raise ValueError("AZURE_FOUNDRY_PROJECT_ENDPOINT environment variable is required")
        if not self.api_key:
            raise ValueError("AZURE_FOUNDRY_API_KEY environment variable is required for BYOK")
        
        # Convert Foundry project endpoint to OpenAI-compatible base URL
        # Foundry endpoint: https://.../api/projects/foundryProject
        # OpenAI base URL: https://.../openai/v1/
        if '/api/projects/' in foundry_endpoint:
            base_parts = foundry_endpoint.split('/api/projects/')[0]
            self.base_url = f"{base_parts}/openai/v1/"
        else:
            self.base_url = foundry_endpoint if foundry_endpoint.endswith('/') else f"{foundry_endpoint}/"
            if not self.base_url.endswith('/openai/v1/'):
                self.base_url = f"{self.base_url}openai/v1/"
        
        self.client = None
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.client = CopilotClient()
        await self.client.start()
        
        # Create session with BYOK provider configuration for Azure Foundry
        self.session = await self.client.create_session({
            "model": self.model,
            "provider": {
                "type": "openai",
                "base_url": self.base_url,
                "api_key": self.api_key,
                "wire_api": "chat",  # Use "chat" for GPT-4o, "responses" for GPT-5
            },
        })
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.destroy()
        if self.client:
            await self.client.stop()
    
    async def answer_question(self, question):
        """Generate an answer using GitHub Copilot SDK with BYOK
        
        Uses event-based messaging pattern from Copilot SDK:
        - Sends prompt via session.send()
        - Receives response through event handlers
        - Waits for session.idle event to complete
        
        Args:
            question: The question to answer
            
        Returns:
            The agent's answer as a string
        """
        try:
            response_text = ""
            done = asyncio.Event()
            
            def on_event(event):
                nonlocal response_text
                
                if event.type.value == "assistant.message":
                    response_text = event.data.content
                elif event.type.value == "session.idle":
                    done.set()
            
            self.session.on(on_event)
            await self.session.send({"prompt": question})
            await done.wait()
            
            return response_text
        except Exception as e:
            error_message = f"Error calling Copilot SDK: {str(e)}"
            print(error_message)
            return error_message


async def main():
    
    test_questions = [
        "What is 15 + 27?"
    ]
    
    async with GameAgent() as agent:
        for question in test_questions:
            answer = await agent.answer_question(question)
            print(f"Q: {question}")
            print(f"A: {answer}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
