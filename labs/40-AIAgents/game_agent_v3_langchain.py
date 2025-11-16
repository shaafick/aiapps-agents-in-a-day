
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()



class GameAgent:
    """LangChain LLM Agent for RPS Tournament"""
    def __init__(self, player_name=None, openai_api_key=None, model_name=None):
        self.player_name = player_name or os.getenv('DEV_Name', 'default-player')
        self.openai_api_key = openai_api_key or os.getenv('AZURE_OPENAI_API_KEY')
        self.azure_endpoint = os.getenv('AZURE_OPENAI_API_ENDPOINT')
        self.model_name = model_name or os.getenv('AZURE_OPENAI_API_DEPLOYMENT_NAME', 'gpt-4o')
        self.api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        self.agent_name = f"agent_{self.player_name}"
        self.llm = AzureChatOpenAI(
            azure_endpoint=self.azure_endpoint,
            api_key=self.openai_api_key,
            api_version=self.api_version,
            azure_deployment=self.model_name,
            temperature=0.7
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def answer_question(self, question):
        prompt = PromptTemplate.from_template("You are {player_name}, a helpful assistant. Answer the following question: {question}")
        formatted_prompt = prompt.format(player_name=self.player_name, question=question)
        response = self.llm.invoke(formatted_prompt)
        return response.content


if __name__ == "__main__":

    print("Game Agent: Test starting...")
    test_questions = [
        "What is 15 + 27?"
    ]

    with GameAgent() as agent:
        print(f"Player Name: {agent.player_name}")
        print(f"Agent Name: {agent.agent_name}")
        print()

        for question in test_questions:
            answer = agent.answer_question(question)
            print(f"Q: {question}")
            print(f"A: {answer}")
            print()

    print("Game Agent: Test complete")