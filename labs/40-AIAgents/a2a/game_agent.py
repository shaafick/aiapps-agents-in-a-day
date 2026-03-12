"""
Game Agent - A2A Client Implementation
=======================================
This demonstrates Agent-to-Agent (A2A) communication using the a2a-sdk

Prerequisites:
    pip install a2a-sdk httpx

Usage:
    python game_agent.py
    Or via main.py
"""

import os
import asyncio
import uuid
import traceback
import httpx
from dotenv import load_dotenv
from a2a.client import ClientFactory, ClientConfig
from a2a.types import Message, TextPart, Task

load_dotenv()


class GameAgent:
    """Client that connects to Game Tools Agent via A2A protocol"""
    
    def __init__(self, player_name=None):
        self.player_name = player_name or os.getenv('DEV_Name', 'default-player')
        
        server_url = os.getenv('SERVER_URL', 'localhost')
        port = os.getenv('GAME_TOOLS_AGENT_PORT', '8088')
        self.tools_service_url = f"http://{server_url}:{port}"
        
        self.agent_client = None
        self.agent_card = None
        self.httpx_client = None
        
    async def connect_to_tools_service(self):
        """Connect to remote tools agent using A2A protocol
        
        A2A Discovery Process (Modern ClientFactory API):
        1. ClientFactory.connect() discovers the agent card from /.well-known/agent-card
        2. Agent card contains: name, description, capabilities, skills, transport
        3. ClientFactory creates appropriate transport (JSON-RPC, REST, or gRPC)
        4. Returns a Client instance ready for communication
        
        This is the foundation of Agent-to-Agent communication!
        """
        try:
            # Create HTTP client for connection
            self.httpx_client = httpx.AsyncClient(timeout=60.0)
            
            # Create client configuration
            client_config = ClientConfig(httpx_client=self.httpx_client)
            
            # Use ClientFactory to connect to the agent
            # This discovers the agent card and creates the appropriate client
            self.agent_client = await ClientFactory.connect(
                self.tools_service_url,
                client_config=client_config
            )
            
            # Get the agent card from the client
            self.agent_card = await self.agent_client.get_card()
            print(f"✓ Discovered remote agent: {self.agent_card.name}")
            print(f"  Description: {self.agent_card.description}")
            print(f"  Skills: {', '.join([skill.name for skill in self.agent_card.skills])}")
            print(f"✓ A2A connection established to {self.tools_service_url}")
            return True
            
        except Exception as e:
            print(f"⚠️  Cannot connect to tools service: {str(e)}")
            print(f"   Make sure the game tools agent server is running on {self.tools_service_url}")
            traceback.print_exc()
            return False
    
    async def send_message(self, user_message: str) -> str:
        """Send a message to the Game Tools Agent via A2A protocol"""
        
        if not self.agent_client:
            raise RuntimeError("Not connected to tools service. Call connect_to_tools_service() first.")
        
        try:
            print(f"\n[A2A] Sending message to {self.agent_card.name}...")
            
            # Create A2A message
            message = Message(
                messageId=str(uuid.uuid4()),
                role="user",
                parts=[TextPart(text=user_message)]
            )
            
            # Send message and iterate over response events
            # The Client.send_message returns an AsyncIterator[ClientEvent | Message]
            result_text = None
            async for event in self.agent_client.send_message(message):
                # Handle tuple responses (Task, Update) or (Task, Message)
                if isinstance(event, tuple):
                    for item in event:
                        # Check for Task with history or status message
                        if isinstance(item, Task):
                            # First check status message (for completed/failed tasks)
                            if item.status and item.status.message:
                                status_msg = item.status.message
                                if status_msg.parts:
                                    for part in status_msg.parts:
                                        # Part is a RootModel, access via .root
                                        if hasattr(part, 'root') and isinstance(part.root, TextPart) and part.root.text:
                                            result_text = part.root.text
                                            break
                                        elif isinstance(part, TextPart) and part.text:
                                            result_text = part.text
                                            break
                            
                            # Then check history for agent responses
                            if not result_text and item.history:
                                # Get the last message in history (agent's response)
                                for msg in reversed(item.history):
                                    if msg.role == "agent" and msg.parts:
                                        for part in msg.parts:
                                            # Handle RootModel wrapper
                                            if hasattr(part, 'root') and isinstance(part.root, TextPart) and part.root.text:
                                                result_text = part.root.text
                                                break
                                            elif isinstance(part, TextPart) and part.text:
                                                result_text = part.text
                                                break
                                        if result_text:
                                            break
                        # Check for Message
                        elif isinstance(item, Message):
                            print(f"[A2A DEBUG] Found Message in tuple with {len(item.parts)} parts")
                            if item.parts:
                                for part in item.parts:
                                    if isinstance(part, TextPart) and part.text:
                                        result_text = part.text
                                        print(f"[A2A] Received response ({len(result_text)} chars): {result_text}")
                                        break
                            if result_text:
                                break
                
                # Check if it's a direct Task response
                elif isinstance(event, Task):
                    print(f"[A2A DEBUG] Direct Task, status: {event.status}")
                    if event.history:
                        for msg in reversed(event.history):
                            if msg.role == "agent" and msg.parts:
                                for part in msg.parts:
                                    if isinstance(part, TextPart) and part.text:
                                        result_text = part.text
                                        print(f"[A2A] Received response ({len(result_text)} chars): {result_text}")
                                        break
                                if result_text:
                                    break
                
                # Check if it's a Message response
                elif isinstance(event, Message):
                    print(f"[A2A DEBUG] Message has {len(event.parts)} parts")
                    if event.parts:
                        for part in event.parts:
                            if isinstance(part, TextPart) and part.text:
                                result_text = part.text
                                print(f"[A2A] Received response ({len(result_text)} chars): {result_text}")
                                break
            
            return result_text if result_text else "No response received from agent"
            
        except Exception as e:
            print(f"[A2A] Error sending message: {str(e)}")
            traceback.print_exc()
            return f"Error: {str(e)}"
    
    async def __aenter__(self):
        await self.connect_to_tools_service()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.httpx_client:
            await self.httpx_client.aclose()


async def main():
    """Interactive client for testing A2A communication"""
    print("=" * 60)
    print("Rock-Paper-Scissors Game Agent (A2A Demo)")
    print("=" * 60)
    print("Connecting to Game Tools Agent via A2A protocol...")
    print()
    
    async with GameAgent() as client:
        print()
        print("Game Agent ready! You can ask about:")
        print("  - Calculations (e.g., 'What is 5 + 7?')")
        print("  - RPS rules (e.g., 'Does rock beat scissors?')")
        print("  - Tournament info (e.g., 'What are the tournament rules?')")
        print()
        print("Type your questions or 'quit' to exit.")
        print("=" * 60)
        print()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                answer = await client.send_message(user_input)
                print(f"Agent: {answer}")
                print()
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGame Agent stopped by user")
