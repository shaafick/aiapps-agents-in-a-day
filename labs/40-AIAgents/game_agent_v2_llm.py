import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

load_dotenv()

class GameAgent:
    """Microsoft Foundry Agent service for RPS Tournament"""
    
    def __init__(self, project_endpoint=None, model_deployment_name=None, player_name=None):
        self.project_endpoint = project_endpoint or os.getenv('AZURE_FOUNDRY_PROJECT_ENDPOINT')
        self.model_deployment_name = model_deployment_name or os.getenv('AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME')
        self.player_name = player_name or os.getenv('DEV_Name', 'default-player')
        self.player_name = self.player_name + "_v2"
        
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
            self.agent = existing_agent
            print(f"Reusing existing agent: {self.agent_name}")
        else:
            self.agent = self.project_client.agents.create_agent(
                model=self.model_deployment_name,
                name=self.agent_name,
                instructions=f"You are {self.player_name}, a helpful assistant that can answer questions and play Rock-Paper-Scissors games."
            )
            print(f"Created new agent: {self.agent_name}")
        
        self.thread = self.project_client.agents.threads.create()
    
    def _call_azure_ai_agent(self, message):
        """Call Microsoft Foundry Agent service"""
        self.project_client.agents.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message
        )
        
        run = self.project_client.agents.runs.create_and_process(
            thread_id=self.thread.id,
            agent_id=self.agent.id
        )
        
        messages = self.project_client.agents.messages.list(thread_id=self.thread.id)
        
        for message in messages:
            if message.role == "assistant":
                return message.content[0].text.value
        
        return "No response"
    
    def answer_question(self, question):
        """Generate an answer to the question using Microsoft Foundry Agent service"""
        if not self.agent:
            self._setup_agent()
        return self._call_azure_ai_agent(question)


if __name__ == "__main__":
 
    print("Game Agent: Test starting...")
    
    with GameAgent() as agent:
        answer = agent.answer_question('hello, how are you?')
        print(f"Agent: {answer}")
        print()
    
    print("Game Agent: Test complete")