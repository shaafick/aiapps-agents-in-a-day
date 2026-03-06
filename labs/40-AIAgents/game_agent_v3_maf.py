import os
import asyncio
from dotenv import load_dotenv

# Workaround for agent-framework 1.0.0rc1 compatibility issue
# MUST be applied BEFORE importing agent_framework
from opentelemetry.semconv_ai import SpanAttributes
SpanAttributes.LLM_SYSTEM = "gen_ai.system"
SpanAttributes.LLM_REQUEST_MODEL = "gen_ai.request.model"
SpanAttributes.LLM_REQUEST_MAX_TOKENS = "gen_ai.request.max_tokens"
SpanAttributes.LLM_REQUEST_TEMPERATURE = "gen_ai.request.temperature"
SpanAttributes.LLM_REQUEST_TOP_P = "gen_ai.request.top_p"
SpanAttributes.LLM_RESPONSE_MODEL = "gen_ai.response.model"
SpanAttributes.LLM_TOKEN_TYPE = "gen_ai.token.type"

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

load_dotenv(override=True)


INSTRUCTIONS = """You are a helpful game assistant that can do math and play Rock-Paper-Scissors.

For math questions, calculate the answer yourself.
For RPS games, randomly choose rock, paper, or scissors, compare with the player's move, and determine the winner.

Be friendly and concise in your responses."""


async def main():
    print("=" * 60)
    print("Microsoft Agent Framework - Game Agent")
    print("=" * 60)
    print("You can:")
    print("  - Ask math questions (e.g., 'What is 15 + 27?')")
    print("  - Play Rock-Paper-Scissors (e.g., 'I choose rock')")
    print("  - Type 'exit' or 'quit' to end")
    print("=" * 60)
    print()
    
    endpoint = os.environ.get("AZURE_FOUNDRY_PROJECT_ENDPOINT") or os.environ.get("AZURE_OPENAI_API_ENDPOINT")
    model = os.environ.get("AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-4o")
    
    if not endpoint:
        print("Configuration Error:")
        print("Please ensure AZURE_FOUNDRY_PROJECT_ENDPOINT or AZURE_OPENAI_API_ENDPOINT is set in your .env file")
        return
    
    print(f"Using endpoint: {endpoint}")
    print(f"Using model: {model}")
    print()
    
    credential = DefaultAzureCredential()
    
    client = AzureOpenAIResponsesClient(
        project_endpoint=endpoint,
        deployment_name=model,
        credential=credential
    )
    
    agent = client.as_agent(
        name="GameAgent",
        instructions=INSTRUCTIONS
    )
    
    session = agent.create_session()
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            response = await agent.run(user_input, session=session)
            print(f"Agent: {response}")
            print()
            
        except Exception as e:
            print(f"Error: {e}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
