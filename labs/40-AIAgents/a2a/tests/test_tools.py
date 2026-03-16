"""Quick test of the tool functions"""
import sys
import os

# Add parent directory to path so we can import from a2a
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and test the get_tournament_info function
from game_tools_agent.agent import create_game_tools_agent
import asyncio

async def test_tournament_info():
    # Read the rulebook directly (it's in parent directory)
    rulebook_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'game_rulebook.txt')
    print(f"Rulebook path: {rulebook_path}")
    print(f"Exists: {os.path.exists(rulebook_path)}")
    
    if os.path.exists(rulebook_path):
        with open(rulebook_path, 'r') as f:
            content = f.read()
        print(f"\nRulebook content length: {len(content)} characters")
        print(f"First 500 chars:\n{content[:500]}")
    
    # Now test via the tool (we need to extract the function)
    # Let's just manually test the parsing logic
    print("\n" + "="*60)
    print("Testing get_tournament_info parsing:")
    print("="*60)
    
    with open(rulebook_path, 'r') as f:
        rulebook_content = f.read()
    
    query = "tournament rules"
    query_lower = query.lower()
    
    # This is the code path for 'rule' in query
    if 'rule' in query_lower or 'beat' in query_lower or 'win' in query_lower:
        lines = rulebook_content.split('\n')
        rules = []
        capture = False
        for line in lines:
            if 'game rules' in line.lower():
                capture = True
                print(f"[CAPTURE START] Found header: {repr(line)}")
                continue
            elif capture and line.strip() and not line.startswith('##'):
                if line.startswith('#'):
                    print(f"[CAPTURE END] Hit single # header: {repr(line)}")
                    break
                print(f"[CAPTURING] {repr(line)}")
                rules.append(line)
            elif capture and line.startswith('##'):
                print(f"[CAPTURE END] Hit ## header: {repr(line)}")
                break
        
        result = '\n'.join(rules)
        print(f"\n[RESULT] Length: {len(result)} characters")
        print(f"[RESULT] Content:\n{result}")
        print(f"[RESULT] Repr: {repr(result)}")

if __name__ == "__main__":
    asyncio.run(test_tournament_info())
