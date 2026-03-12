"""
Game Tools Agent Executor - A2A Protocol Implementation
========================================================
Implements AgentExecutor pattern for game tools (calculate, RPS rules, tournament info)

Prerequisites:
    pip install a2a-sdk

Usage:
    from game_tools_agent.agent_executor import create_game_tools_executor
    executor = create_game_tools_executor(agent_card)
"""

import os
import ast
import operator
from a2a.server.events.event_queue import EventQueue
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.tasks import TaskUpdater
from a2a.utils import new_agent_text_message
from a2a.types import AgentCard, Part, TaskState


class GameToolsExecutor(AgentExecutor):
    """Executor for game tools agent that processes RPS tournament queries"""

    def __init__(self, card: AgentCard):
        self._card = card

    def _calculate(self, expression: str) -> str:
        """Calculate mathematical expressions safely"""
        print(f"[A2A Tool] calculate() invoked with: {expression}")
        allowed_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }
        
        def _eval(node):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in allowed_ops:
                return allowed_ops[type(node.op)](_eval(node.left), _eval(node.right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_ops:
                return allowed_ops[type(node.op)](_eval(node.operand))
            raise ValueError(f"Unsupported expression")
        
        try:
            tree = ast.parse(expression, mode="eval")
            return str(_eval(tree.body))
        except Exception as e:
            return f"Error: {str(e)}"

    def _rps_rules(self, question: str) -> str:
        """Answer Rock-Paper-Scissors game rules questions"""
        print(f"[A2A Tool] rps_rules() invoked with: {question}")
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

    def _get_tournament_info(self, query: str) -> str:
        """Get information about the RPS tournament format, scoring, and rules from the rulebook"""
        print(f"[A2A Tool] get_tournament_info() invoked with: {query}")
        try:
            # Read the game rulebook (look in parent directory)
            rulebook_path = os.path.join(os.path.dirname(__file__), '..', 'game_rulebook.txt')
            if not os.path.exists(rulebook_path):
                rulebook_path = os.path.join(os.path.dirname(__file__), 'game_rulebook.txt')
            
            with open(rulebook_path, 'r') as f:
                rulebook_content = f.read()
            
            # Return relevant sections based on query
            query_lower = query.lower()
            
            if 'score' in query_lower or 'point' in query_lower:
                # Extract scoring information
                lines = rulebook_content.split('\n')
                scoring = []
                capture = False
                for line in lines:
                    if 'scoring system' in line.lower() or 'tournament format' in line.lower():
                        capture = True
                    elif capture and line.strip() and not line.startswith('##'):
                        if line.startswith('#'):
                            break
                        scoring.append(line)
                    elif capture and line.startswith('##') and len(scoring) > 0:
                        break
                result = '\n'.join(scoring)
                return f"Tournament scoring:\n{result}"
            
            elif 'format' in query_lower or 'round' in query_lower:
                # Extract tournament format
                lines = rulebook_content.split('\n')
                format_info = []
                capture = False
                for line in lines:
                    if 'tournament format' in line.lower():
                        capture = True
                    elif capture and line.strip() and not line.startswith('##'):
                        if line.startswith('#'):
                            break
                        format_info.append(line)
                    elif capture and line.startswith('##') and len(format_info) > 0:
                        break
                result = '\n'.join(format_info)
                return f"Tournament format:\n{result}"
            
            elif 'rule' in query_lower or 'beat' in query_lower or 'win' in query_lower:
                # Extract game rules
                lines = rulebook_content.split('\n')
                rules = []
                capture = False
                for line in lines:
                    if 'game rules' in line.lower():
                        capture = True
                        continue
                    elif capture and line.strip() and not line.startswith('##'):
                        if line.startswith('#'):
                            break
                        rules.append(line)
                    elif capture and line.startswith('##'):
                        break
                
                result = '\n'.join(rules)
                return f"Game rules:\n{result}"
            
            else:
                # Return high-level summary
                return """Tournament information:

Format: 5 rounds total - each round has a question + RPS move

Scoring:
- Correct answer: +10 points
- RPS win: +20 points
- RPS tie: +10 points
- RPS loss: +0 points

Game Rules:
- Rock beats Scissors (crushes)
- Paper beats Rock (covers)
- Scissors beats Paper (cuts)
- Same moves = tie"""
                
        except Exception as e:
            return f"Error reading tournament info: {str(e)}"

    def _process_message(self, user_message: str) -> str:
        """Process a user message and determine which tool to use"""
        message_lower = user_message.lower()
        
        # Check for calculation requests
        if any(keyword in message_lower for keyword in ['calculate', 'compute', 'what is', '+', '-', '*', '/', '**', 'math']):
            # Try to extract expression or use whole message
            if 'calculate' in message_lower:
                parts = message_lower.split('calculate', 1)
                expression = parts[1].strip() if len(parts) > 1 else user_message
            elif 'compute' in message_lower:
                parts = message_lower.split('compute', 1)
                expression = parts[1].strip() if len(parts) > 1 else user_message
            elif 'what is' in message_lower:
                parts = message_lower.split('what is', 1)
                expression = parts[1].strip().rstrip('?') if len(parts) > 1 else user_message
            else:
                expression = user_message
            return self._calculate(expression)
        
        # Check for RPS rules requests
        elif any(keyword in message_lower for keyword in ['rock', 'paper', 'scissors', 'beat', 'win', 'vs', 'versus']):
            return self._rps_rules(user_message)
        
        # Check for tournament info requests
        elif any(keyword in message_lower for keyword in ['tournament', 'score', 'scoring', 'format', 'round', 'point']):
            return self._get_tournament_info(user_message)
        
        else:
            return "I can help with: calculations, Rock-Paper-Scissors rules, and tournament information. Please ask about one of these topics."

    async def _process_request(self, message_parts: list[Part], context_id: str, task_updater: TaskUpdater) -> None:
        """Process a user request"""
        
        try:
            # Extract text from message parts
            user_message = ""
            for part in message_parts:
                if hasattr(part.root, 'text') and part.root.text:
                    user_message = part.root.text
                    break
            
            if not user_message:
                await task_updater.failed(
                    message=new_agent_text_message("No message text found", context_id=context_id)
                )
                return

            # Update status to working
            await task_updater.update_status(
                TaskState.working,
                message=new_agent_text_message('Game Tools Agent is processing...', context_id=context_id),
            )

            # Process the message and get response
            response = self._process_message(user_message)

            # Complete the task with the response
            await task_updater.complete(
                message=new_agent_text_message(response, context_id=context_id)
            )

        except Exception as e:
            print(f'Game Tools Agent: Error processing request - {e}')
            await task_updater.failed(
                message=new_agent_text_message(
                    f"Game Tools Agent failed to process the request: {str(e)}", 
                    context_id=context_id
                )
            )

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """Execute the agent task"""
        
        # Create task updater
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.submit()

        # Start working
        await updater.start_work()

        # Process the request
        await self._process_request(context.message.parts, context.context_id, updater)

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Cancel the agent task"""
        print(f'Game Tools Agent: Cancelling execution for context {context.context_id}')

        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.failed(
            message=new_agent_text_message('Task cancelled by user', context_id=context.context_id)
        )


def create_game_tools_executor(card: AgentCard) -> GameToolsExecutor:
    """Create a game tools executor instance"""
    return GameToolsExecutor(card)
