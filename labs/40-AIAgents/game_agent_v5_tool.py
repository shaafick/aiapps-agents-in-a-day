import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import FunctionTool
import time

load_dotenv()


class GameAgent:
    """Azure AI Foundry Agent service for RPS Tournament"""
    
    def __init__(self, project_endpoint=None, model_deployment_name=None, player_name=None):
        self.project_endpoint = project_endpoint or os.getenv('AZURE_FOUNDRY_PROJECT_ENDPOINT')
        self.model_deployment_name = model_deployment_name or os.getenv('AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME')
        self.player_name = player_name or os.getenv('DEV_Name', 'default-player')
        self.player_name = self.player_name + "_v5"
        
        self.project_client = AIProjectClient(
            endpoint=self.project_endpoint,
            credential=DefaultAzureCredential()
        )
        
        self.agent = None
        self.thread = None
        self._client_context = None
        self.agent_name = f"agent_{self.player_name}"
    
    def __enter__(self):
        self._client_context = self.project_client.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client_context:
            return self.project_client.__exit__(exc_type, exc_val, exc_tb)
    
    def _find_existing_agent(self):
        """Find existing agent by name"""
     
        agents = self.project_client.agents.list_agents()
        for agent in agents:
            if agent.name == self.agent_name:
                return agent
 
        return None
    
    def cleanup_old_agents(self):
        """Clean up old agents with the same name (optional maintenance method)"""
        try:
            agents = self.project_client.agents.list_agents()
            for agent in agents:
                if agent.name == self.agent_name and agent.id != (self.agent.id if self.agent else None):
                    self.project_client.agents.delete(agent.id)
        except Exception:
            pass
    
    def _setup_agent(self):
        """Setup the Azure AI agent - reuse existing or create new"""
        existing_agent = self._find_existing_agent()
        
        if existing_agent:
            self.project_client.agents.delete_agent(existing_agent.id)
            print(f"Deleted existing agent: {self.agent_name}")
        
        tools = self._setup_tools()
        self.agent = self.project_client.agents.create_agent(
            model=self.model_deployment_name,
            name=self.agent_name,
            instructions=f"You are {self.player_name}, a helpful assistant that can answer questions and play Rock-Paper-Scissors games.",
            tools=tools
        )
        print(f"Created new agent: {self.agent_name}")
        
        self.thread = self.project_client.agents.threads.create()
    
    def _call_azure_ai_agent(self, message):
        """Call Azure AI Foundry Agent service"""
        self.project_client.agents.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message
        )
        
        run = self.project_client.agents.runs.create(
            thread_id=self.thread.id,
            agent_id=self.agent.id
        )
        
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = self.project_client.agents.runs.get(thread_id=self.thread.id, run_id=run.id)
            
            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for tool_call in tool_calls:
                    if tool_call.function.name == "math_tool_function":
                        import json
                        args = json.loads(tool_call.function.arguments)
                        output = GameAgent.math_tool_function(args.get("expression", ""))
                        tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
                self.project_client.agents.runs.submit_tool_outputs(thread_id=self.thread.id, run_id=run.id, tool_outputs=tool_outputs)
        
        messages = self.project_client.agents.messages.list(thread_id=self.thread.id)
        
        for message in messages:
            if message.role == "assistant":
                return message.content[0].text.value
        
        return "No response"
    
    
    def answer_question(self, question):
        """Generate an answer to the question using Azure AI Foundry Agent service"""
        if not self.agent:
            self._setup_agent()
        return self._call_azure_ai_agent(question)

    
    @staticmethod
    def math_tool_function(expression: str) -> str:
        """
        Calculate mathematical expressions.

        :param expression: The mathematical expression to calculate.
        :return: Result of the calculation as a string.
        """
        try:
            print('math_tool_function')
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"
        
    def _setup_tools(self):
        """Setup tool functions for the agent"""
        user_functions = {GameAgent.math_tool_function}
        functions = FunctionTool(functions=user_functions)
        return functions.definitions


if __name__ == "__main__":

    print("Game Agent: Test starting...")
    test_questions = [
        "What is (15 + 27) ^ 2 / 82 ?"
    ]
    
    with GameAgent() as agent:
        for question in test_questions:
            answer = agent.answer_question(question)
            print(f"Q: {question}")
            print(f"A: {answer}")
            print()
    
    print("Game Agent: Test complete")