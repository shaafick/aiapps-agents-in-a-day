"""
Game Tools Agent Server - A2A Service Implementation
====================================================
Starlette-based A2A protocol service providing game tools

Prerequisites:
    pip install a2a-sdk starlette sse-starlette uvicorn

Usage:
    python game_tools_agent/server.py
    Or via main.py
    
This is Agent #1 in the A2A architecture - provides tools to other agents.
"""

import os
import uvicorn
from typing import AsyncIterable

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from game_tools_agent.agent_executor import create_game_tools_executor

load_dotenv()

host = os.environ.get("SERVER_URL", "localhost")
port = os.environ.get("GAME_TOOLS_AGENT_PORT", "8088")

# Define agent skills
skills = [
    AgentSkill(
        id='calculate',
        name='Calculate',
        description='Calculate mathematical expressions (supports +, -, *, /, **)',
        tags=['math', 'calculator', 'arithmetic'],
        examples=[
            'What is 5 + 3?',
            'Calculate 2 ** 8',
            'Compute 15 * 7',
        ],
    ),
    AgentSkill(
        id='rps_rules',
        name='RPS Rules',
        description='Answer Rock-Paper-Scissors game rules questions',
        tags=['game', 'rps', 'rules'],
        examples=[
            'Does rock beat scissors?',
            'What beats paper?',
            'Rock vs paper - who wins?',
        ],
    ),
    AgentSkill(
        id='tournament_info',
        name='Tournament Info',
        description='Provide RPS tournament format, scoring, and detailed rules',
        tags=['tournament', 'scoring', 'format'],
        examples=[
            'What are the tournament rules?',
            'How is scoring done?',
            'What is the tournament format?',
        ],
    ),
]

# Create agent card
agent_card = AgentCard(
    name='GameToolsAgent',
    description='A specialized assistant for Rock-Paper-Scissors tournament. '
    'I can help with calculations, game rules, and tournament information.',
    url=f'http://{host}:{port}/',
    version='1.0.0',
    default_input_modes=['text'],
    default_output_modes=['text'],
    capabilities=AgentCapabilities(),
    skills=skills,
)

# Create agent executor
agent_executor = create_game_tools_executor(agent_card)

# Create request handler
request_handler = DefaultRequestHandler(
    agent_executor=agent_executor, task_store=InMemoryTaskStore()
)

# Create A2A application
a2a_app = A2AStarletteApplication(
    agent_card=agent_card, http_handler=request_handler
)

# Get routes
routes = a2a_app.routes()

# Add health check endpoint
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse('Game Tools Agent is running!')

routes.append(Route(path='/health', methods=['GET'], endpoint=health_check))

# Create Starlette app
app = Starlette(routes=routes)


def main():
    print(f"✓ Game Tools Agent starting on http://{host}:{port}")
    print(f"  Agent card: http://{host}:{port}/.well-known/agent-card")
    print(f"  Skills: calculate, rps_rules, tournament_info")
    
    # Run the server
    uvicorn.run(app, host=host, port=int(port))


if __name__ == '__main__':
    main()
