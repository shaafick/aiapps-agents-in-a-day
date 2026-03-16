import os
import asyncio
from dotenv import load_dotenv
from copilot import CopilotClient, SessionConfig, MessageOptions, PermissionHandler

load_dotenv()


class GameAgent:
    """Game agent using GitHub Copilot SDK with Azure Foundry BYOK"""
    
    def __init__(self, player_name=None, model=None):
        self.player_name = player_name or os.getenv('DEV_Name', 'default-player')
        self.model = model or os.getenv('AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME', 'gpt-4o')
        self.api_key = os.getenv('AZURE_FOUNDRY_API_KEY')
        foundry_endpoint = os.getenv('AZURE_FOUNDRY_PROJECT_ENDPOINT')
        
        if not foundry_endpoint or not self.api_key:
            raise ValueError("AZURE_FOUNDRY_PROJECT_ENDPOINT and AZURE_FOUNDRY_API_KEY are required")
        
        self.base_url = foundry_endpoint.rstrip('/')
        self.client = None
        self.session = None
    
    async def __aenter__(self):
        self.client = CopilotClient()
        await self.client.start()
        
        self.session = await self.client.create_session(SessionConfig(
            model=self.model,
            provider={
                "type": "azure",
                "base_url": self.base_url,
                "api_key": self.api_key,
                "azure": {"api_version": "2024-10-21"},
            },
            on_permission_request=PermissionHandler.approve_all,
        ))
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.destroy()
        if self.client:
            await self.client.stop()
    
    async def answer_question(self, question):
        """Send a question and get the response"""
        response = await self.session.send_and_wait(MessageOptions(prompt=question))
        return response.data.content if response else ""

async def main():
    """Test the GameAgent with sample questions"""
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
