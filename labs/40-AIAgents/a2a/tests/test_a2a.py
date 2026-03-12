"""
Quick test script for A2A communication
"""
import asyncio
import subprocess
import time
import sys
import os

# Add parent directory to path so we can import game_agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_agent import GameAgent

async def test_a2a():
    """Test the A2A communication"""
    
    # Start the server
    print("Starting game tools server...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "game_tools_agent.server:app", "--port", "8088"]
        # stdout and stderr will go to console so we can see debug output
    )
    
    # Wait for server to be ready
    time.sleep(3)
    
    try:
        # Create game agent and connect
        print("\nCreating game agent...")
        agent = GameAgent()
        
        if await agent.connect_to_tools_service():
            
            # Test multiple questions
            questions = [
                "What are the tournament rules?",  # Should use tournament_info
                "What is 5 + 7 * 3?",              # Should use calculate
                "Does rock beat scissors?"          # Should use rps_rules
            ]
            
            for question in questions:
                print("\n" + "="*60)
                print(f"Testing: {question}")
                print("="*60)
                
                answer = await agent.send_message(question)
                print(f"\nAnswer:\n{answer}")
                print("="*60)
        else:
            print("Failed to connect to tools service")
    
    finally:
        # Cleanup
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(test_a2a())

if __name__ == "__main__":
    asyncio.run(test_a2a())
