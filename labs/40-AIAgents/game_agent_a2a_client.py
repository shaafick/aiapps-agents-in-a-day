"""
Game Agent with A2A Protocol Client (Alternative Implementation)
=================================================================
NOTE: This is an alternative A2A implementation for reference.
For the main lab exercise, use game_agent_v7_a2a_logo.py and game_agent_v7_a2a_rps.py

This implements the RPS game agent that connects to the logo agent via A2A protocol.

Prerequisites:
    pip install agent-framework agent-framework-azure-ai a2a-client httpx

Usage:
    1. Start the logo agent service first:
       python game_agent_v7_a2a_logo.py
    
    2. Run this agent:
       python game_agent_a2a_client.py
       
Note: This implementation expects the logo service on port 8001 instead of 8088.
"""

import ast
import operator
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


class GameAgentA2A:
    
    def __init__(self, player_name=None, logo_agent_url="http://localhost:8001"):
        self.endpoint = os.getenv('AZURE_FOUNDRY_PROJECT_ENDPOINT')
        self.deployment_name = os.getenv('AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME')
        self.player_name = player_name or os.getenv('DEV_Name', 'default-player')
        self.logo_agent_url = logo_agent_url
        
        self.agent = None
        self.logo_agent = None
        self.credential = None
        
    async def connect_to_logo_agent(self):
        """Connect to the remote logo agent via A2A protocol"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as http_client:
                # Discover the remote agent's capabilities
                resolver = A2ACardResolver(
                    httpx_client=http_client, 
                    base_url=self.logo_agent_url
                )
                agent_card = await resolver.get_agent_card()
                print(f"✓ Discovered logo agent: {agent_card.name}")
        
            # Create A2A proxy agent
            self.logo_agent = A2AAgent(
                name=agent_card.name,
                agent_card=agent_card,
                url=f"{self.logo_agent_url}/a2a/logo/v1/message:stream"
            )
            
            print(f"✓ Connected to logo agent via A2A protocol")
            return True
            
        except Exception as e:
            print(f"⚠️  Can't find my logo agent :( - {str(e)}")
            print(f"   Make sure logo_agent_a2a_service.py is running on {self.logo_agent_url}")
            return False
    
    async def create_main_agent(self):
        """Create the main game agent with tools"""
        self.credential = DefaultAzureCredential()
        
        chat_client = AzureOpenAIChatClient(
            endpoint=self.endpoint,
            deployment_name=self.deployment_name,
            credential=self.credential
        )
        
        # Define math tool
        def calculate(expression: str) -> str:
            allowed_ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.Mod: operator.mod,
                ast.USub: operator.neg,
            }

            def eval_node(node):
                if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                    return node.value
                if isinstance(node, ast.BinOp) and type(node.op) in allowed_ops:
                    return allowed_ops[type(node.op)](eval_node(node.left), eval_node(node.right))
                if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_ops:
                    return allowed_ops[type(node.op)](eval_node(node.operand))

            return str(eval_node(ast.parse(expression, mode='eval').body))
        
        # Build tools list
        tools = [calculate]
        
        # Add logo agent as a tool if connected
        if self.logo_agent:
            logo_tool = self.logo_agent.as_tool(
                name="detect_logo",
                description="Detect the name of a logo or brand from an image URL"
            )
            tools.append(logo_tool)
        
        # Create main agent
        self.agent = Agent(
            name=f"GameAgent_{self.player_name}",
            chat_client=chat_client,
            instructions=f"""You are {self.player_name}, a helpful assistant that can answer 
            questions and play Rock-Paper-Scissors games. Keep answers short and precise.""",
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
        # Connect to logo agent
        await self.connect_to_logo_agent()
        # Create main agent
        await self.create_main_agent()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.credential:
            await self.credential.close()


async def main():
    print("=" * 60)
    print("Rock-Paper-Scissors Game Agent (A2A Protocol)")
    print("=" * 60)
    print()
    
    test_questions = [
        "What is 15 * 23?",
        "What is this logo? https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.png",
        "If I play Rock and my opponent plays Scissors, who wins?"
    ]
    
    async with GameAgentA2A() as agent:
        print()
        print("Testing agent capabilities:")
        print("-" * 60)
        
        for question in test_questions:
            print(f"\nQ: {question}")
            answer = await agent.answer_question(question)
            print(f"A: {answer}")
        
        print()
        print("-" * 60)
        print("All tests complete!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAgent stopped by user")
