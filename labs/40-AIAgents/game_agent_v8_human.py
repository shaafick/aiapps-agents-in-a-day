import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import FunctionTool, FileSearchTool, FilePurpose
from azure.ai.agents.models import ConnectedAgentTool, MessageRole
from azure.ai.agents.models import (
    ListSortOrder,
    McpTool,
    RequiredMcpToolCall,
    RunStepActivityDetails,
    SubmitToolApprovalAction,
    ToolApproval,
)
import time

load_dotenv()


class GameAgent:
    """Microsoft Foundry Agent service for RPS Tournament with Human-in-the-Loop"""
    
    def __init__(self, project_endpoint=None, model_deployment_name=None, player_name=None):
        self.project_endpoint = project_endpoint or os.getenv('AZURE_FOUNDRY_PROJECT_ENDPOINT')
        self.model_deployment_name = model_deployment_name or os.getenv('AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME')
        self.player_name = player_name or os.getenv('DEV_Name', 'default-player')
        self.player_name = self.player_name + "_v8"
        
        self.project_client = AIProjectClient(
            endpoint=self.project_endpoint,
            credential=DefaultAzureCredential()
        )
        
        self.agent_name = f"rps-game-agent-human-loop-{self.player_name}"
        self.agent = None
        self.thread = None
        self._client_context = None
    
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
            instructions=f"You are {self.player_name}, a helpful assistant that can answer questions and play Rock-Paper-Scissors games. When you need to use tools, ask for human approval first.",
            tools=tools
        )
        print(f"Created new agent: {self.agent_name}")
        
        self.thread = self.project_client.agents.threads.create()
    
    def _request_human_approval(self, tool_call):
        """Request human approval for tool execution"""
        print("\n" + "="*60)
        print("🤖 AGENT REQUESTING TOOL APPROVAL")
        print("="*60)
        print(f"Tool Name: {tool_call.function.name}")
        print(f"Tool Arguments: {tool_call.function.arguments}")
        print(f"Tool Call ID: {tool_call.id}")
        print("-"*60)
        
        # Parse and display arguments in a readable format
        try:
            import json
            args = json.loads(tool_call.function.arguments)
            print("Tool will be called with:")
            for key, value in args.items():
                print(f"  {key}: {value}")
        except:
            print(f"Raw arguments: {tool_call.function.arguments}")
        
        print("-"*60)
        
        # Ask for human approval
        while True:
            response = input("Do you want to approve this tool call? (y/yes/n/no): ").lower().strip()
            if response in ['y', 'yes']:
                print("✅ Tool call APPROVED by human")
                return True
            elif response in ['n', 'no']:
                print("❌ Tool call REJECTED by human")
                return False
            else:
                print("Please enter 'y/yes' to approve or 'n/no' to reject.")
    
    def _call_azure_ai_agent(self, message):
        """Call Microsoft Foundry Agent service with human-in-the-loop approval"""
        self.project_client.agents.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message
        )
        
        run = self.project_client.agents.runs.create(
            thread_id=self.thread.id,
            agent_id=self.agent.id
        )
        print(f"Created run, ID: {run.id}")
        
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = self.project_client.agents.runs.get(thread_id=self.thread.id, run_id=run.id)
            print(f"🔍 DEBUG: Run status: {run.status}")
            
            # Debug: Show all available attributes on run
            if run.status == "requires_action":
                print(f"🔍 DEBUG: run.required_action type: {type(run.required_action)}")
                print(f"🔍 DEBUG: run.required_action attributes: {dir(run.required_action)}")
                if hasattr(run.required_action, '__dict__'):
                    print(f"🔍 DEBUG: run.required_action dict: {vars(run.required_action)}")
                
                # Microsoft Foundry currently uses submit_tool_outputs for tool execution
                # We'll implement human approval by intercepting the tool calls before execution
                if hasattr(run.required_action, 'submit_tool_outputs'):
                    print("🔄 Processing tool calls with human approval...")
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    tool_outputs = []
                    
                    for tool_call in tool_calls:
                        # Request human approval before executing each tool
                        approved = self._request_human_approval(tool_call)
                        
                        if approved:
                            # Execute the tool if approved
                            if tool_call.function.name == "math_tool_function":
                                import json
                                args = json.loads(tool_call.function.arguments)
                                output = GameAgent.math_tool_function(args.get("expression", ""))
                                tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
                                print(f"✅ Executed tool: {tool_call.function.name}")
                            else:
                                # Handle other tools if any
                                tool_outputs.append({"tool_call_id": tool_call.id, "output": "Tool execution not implemented"})
                        else:
                            # If not approved, send a rejection message
                            tool_outputs.append({"tool_call_id": tool_call.id, "output": "Tool execution rejected by human"})
                            print(f"❌ Rejected tool: {tool_call.function.name}")
                    
                    # Submit all tool outputs (approved executions and rejections)
                    self.project_client.agents.runs.submit_tool_outputs(
                        thread_id=self.thread.id, 
                        run_id=run.id, 
                        tool_outputs=tool_outputs
                    )
                    print("📝 Tool outputs submitted")
        
        print(f"Run completed with status: {run.status}")
        if run.status == "failed":
            print(f"Run failed: {run.last_error}")
            
        # Get the latest messages
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

    
    @staticmethod
    def math_tool_function(expression: str) -> str:
        """
        Calculate mathematical expressions.

        :param expression: The mathematical expression to calculate.
        :return: Result of the calculation as a string.
        """
        try:
            print(f'🧮 Executing math calculation: {expression}')
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
        "What is 15 + 27?"
    ]
    
    with GameAgent() as agent:
        for question in test_questions:
            answer = agent.answer_question(question)
            print(f"Q: {question}")
            print(f"A: {answer}")
            print()
    
    print("Game Agent: Test complete")

