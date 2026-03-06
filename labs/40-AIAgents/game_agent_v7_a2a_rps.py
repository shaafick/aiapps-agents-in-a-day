"""
Game Agent - A2A Client Pattern
================================
Uses Microsoft's A2ACardResolver and A2AAgent for proper A2A communication

Prerequisites:
    pip install agent-framework agent-framework-azure-ai httpx

Usage:
    1. Start logo service: python game_agent_v7_a2a_logo.py
    2. Run this client: python game_agent_v7_a2a_rps.py"""
import os
import asyncio
import httpx
from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.a2a import A2AAgent
from a2a.client import A2ACardResolver
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


class GameAgent:
    
    def __init__(self, player_name=None, logo_service_url="http://localhost:8088"):
        self.endpoint = os.getenv('AZURE_OPENAI_API_ENDPOINT')
        self.deployment_name = os.getenv('AZURE_OPENAI_API_DEPLOYMENT_NAME')
        self.player_name = player_name or os.getenv('DEV_Name', 'default-player')
        self.player_name = self.player_name + "_v6"
        self.logo_service_url = logo_service_url
        
        self.agent = None
        self.logo_agent_proxy = None
        self.credential = None
        
    async def connect_to_logo_service(self):
        """Connect to remote logo agent using official A2A pattern"""
        try:
            # Step 1: Discover the remote agent's capabilities using A2ACardResolver
            async with httpx.AsyncClient(timeout=60.0) as http_client:
                resolver = A2ACardResolver(
                    httpx_client=http_client, 
                    base_url=self.logo_service_url
                )
                agent_card = await resolver.get_agent_card()
                print(f"✓ Discovered remote agent: {agent_card.name}")
            
            # Step 2: Create A2AAgent proxy to communicate with remote agent
            self.logo_agent_proxy = A2AAgent(
                name=agent_card.name,
                agent_card=agent_card,
                url=self.logo_service_url
            )
            
            print(f"✓ Connected to logo service via A2A protocol")
            return True
            
        except Exception as e:
            print(f"⚠️  Cannot connect to logo service: {str(e)}")
            print(f"   Make sure game_agent_v7_a2a_logo.py is running on {self.logo_service_url}")
            return False
    
    async def create_main_agent(self):
        """Create the main game agent with tools"""
        self.credential = DefaultAzureCredential()
        
        chat_client = AzureOpenAIChatClient(
            endpoint=self.endpoint,
            deployment_name=self.deployment_name,
            credential=self.credential
        )
        
        def calculate(expression: str) -> str:
            """Calculate mathematical expressions"""
            try:
                return str(eval(expression))
            except Exception as e:
                return f"Error: {str(e)}"
        
        def rps_rules(question: str) -> str:
            """Answer Rock-Paper-Scissors game rules"""
            rules = {
                "rock beats scissors": "Rock wins",
                "scissors beats paper": "Scissors wins", 
                "paper beats rock": "Paper wins",
                "rock vs paper": "Paper wins",
                "scissors vs rock": "Rock wins",
                "paper vs scissors": "Scissors wins"
            }
            
            question_lower = question.lower()
            for pattern, result in rules.items():
                if pattern in question_lower:
                    return result
            
            return "Rock beats Scissors, Scissors beats Paper, Paper beats Rock"
        
        # Build tools list
        tools = [calculate, rps_rules]
        
        # Add logo agent as a tool using official .as_tool() method
        if self.logo_agent_proxy:
            logo_tool = self.logo_agent_proxy.as_tool(
                name="detect_logo",
                description="Detect the name of a logo or brand from an image URL. Pass the image URL as the message."
            )
            tools.append(logo_tool)
            print("✓ Logo detection tool added")
        
        # Create main agent
        self.agent = Agent(
            name=f"GameAgent_{self.player_name}",
            client=chat_client,
            instructions=f"""You are {self.player_name}, a helpful assistant that can answer 
            questions and play Rock-Paper-Scissors games. 
            
            When asked about a logo in an image, use the detect_logo tool with the image URL.
            Keep answers short and precise.""",
            tools=tools
        )
        
        print(f"✓ Created game agent: {self.agent.name}")
        return self.agent
    
    async def answer_question(self, question: str) -> str:
        """Ask the agent a question"""
        if not self.agent:
            await self.create_main_agent()
        
        result = await self.agent.run(question)
        return result.text
    
    async def __aenter__(self):
        await self.connect_to_logo_service()
        await self.create_main_agent()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.credential:
            await self.credential.close()


async def main():
    print("=" * 60)
    print("Rock-Paper-Scissors Game Agent - Official A2A Client")
    print("=" * 60)
    print("Connecting to Logo Agent via A2A protocol...")
    print()
    
    test_questions = [
        "What is 15 * 23?",
        "What is this logo? https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.png",
        "If I play Rock and my opponent plays Scissors, who wins?"
    ]
    
    async with GameAgent() as agent:
        print()
        print("Running test questions...")
        print("=" * 60)
        print()
        
        for question in test_questions:
            answer = await agent.answer_question(question)
            print(f"Q: {question}")
            print(f"A: {answer}")
            print()
    
    print("=" * 60)
    print("Game Agent: Test complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest stopped by user")
