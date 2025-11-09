import random
import time
import threading
from typing import Optional, List, Dict, Any
from api_client import RPSGameClient
from game_agent import GameAgent

class GameProcessor:
    """Autonomous game agent for RPS Tournament"""
    
    def __init__(self, player_name: str, room_id: int = 1):
        self.player_name = player_name
        self.room_id = room_id
        self.client = RPSGameClient(room_id=room_id)
        self.agent = GameAgent()
        self.player_id: Optional[int] = None
        self.current_round = 1
        self.tournament_status = "Not Started"
        self.round_status = "Not Started"
        self.is_running = False
        self.status_log: List[str] = []
        self.results: List[Dict] = []
        self.last_completed_round = 0
        self.latest_score = 0
        
    def log_status(self, message: str):
        """Add a status message to the log"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.status_log.append(log_message)
        print(log_message)
    
    def register_player(self) -> bool:
        """Register the player with the server"""
        self.log_status(f"Registering player: {self.player_name}")
        
        response = self.client.register_player(self.player_name)
        
        if "error" in response:
            self.log_status(f"Registration failed: {response['error']}")
            return False
        
        if "playerId" in response:
            self.player_id = response["playerId"]
            self.log_status(f"Registration successful! Player ID: {self.player_id}")
            return True
        else:
            self.log_status(f"Registration failed: {response.get('message', 'Unknown error')}")
            return False
    
    def get_move_name(self, move: int) -> str:
        """Convert move number to name"""
        moves = {0: "Rock", 1: "Paper", 2: "Scissors"}
        return moves.get(move, "Unknown")
    
    def monitor_and_play(self):
        """Main game loop - monitors status and plays autonomously"""
        if not self.player_id:
            self.log_status("Error: Player not registered!")
            return
        
        self.is_running = True
        self.log_status("Starting autonomous game monitoring...")
        
        rounds_completed = 0
        max_rounds = 5
        
        while self.is_running and rounds_completed < max_rounds:
            try:
                # Get current status
                status_response = self.client.get_player_status(self.player_id)
                
                if "error" in status_response:
                    self.log_status(f"Error getting status: {status_response['error']}")
                    time.sleep(5)
                    continue
                
                # Update status tracking
                tournament_status = status_response.get("tournamentStatus", 0)
                current_round = status_response.get("currentRound", 1)
                round_status = status_response.get("currentRoundStatus")
                question = status_response.get("currentQuestion")
                can_submit = status_response.get("canSubmit", False)
                
                # Convert status numbers to readable names
                tournament_names = {0: "Pending", 1: "InProgress", 2: "Completed"}
                round_names = {None: "Not Started", 0: "Pending", 1: "InProgress", 2: "Completed"}
                
                self.tournament_status = tournament_names.get(tournament_status, "Unknown")
                self.round_status = round_names.get(round_status, "Unknown")
                self.current_round = current_round
                
                # Log status changes
                status_msg = f"Tournament: {self.tournament_status}, Round {current_round}: {self.round_status}"
                if question:
                    status_msg += f", Question: {question[:50]}..."
                if can_submit:
                    status_msg += ", Can Submit!"
                
                self.log_status(status_msg)
                
                # Handle different states
                if tournament_status == 2:  # Completed
                    self.log_status("Tournament completed!")
                    self.get_final_results()
                    break
                
                if tournament_status == 1 and round_status == 1 and can_submit and question:
                    # Round is in progress and we can submit
                    self.log_status(f"Processing Round {current_round} question...")
                    
                    # Answer the question
                    answer = self.agent.answer_question(question)
                    self.log_status(f"Generated answer: {answer}")
                    
                    # Choose RPS move
                    rps_move = self.choose_rps_move()
                    move_name = self.get_move_name(rps_move)
                    self.log_status(f"Chosen RPS move: {move_name}")
                    
                    # Submit answer and move
                    submit_response = self.client.submit_answer(
                        self.player_id, current_round, answer, rps_move
                    )
                    
                    if "error" in submit_response:
                        self.log_status(f"Submit error: {submit_response['error']}")
                    elif submit_response.get("success"):
                        self.log_status(f"Successfully submitted answer and move for Round {current_round}")
                        rounds_completed = current_round
                        # Fetch updated results after submission
                        time.sleep(1)  # Brief pause to let server process
                        self.get_current_results()
                    else:
                        self.log_status(f"Submit failed: {submit_response.get('message', 'Unknown error')}")
                
                # Wait before next check
                time.sleep(5)
                
            except Exception as e:
                self.log_status(f"Unexpected error: {str(e)}")
                time.sleep(5)
        
        self.is_running = False
        self.log_status("Game monitoring stopped.")

        
    def choose_rps_move(self) -> int:
        """Randomly choose Rock (0), Paper (1), or Scissors (2)"""
        return random.randint(0, 2)
    
    def get_current_results(self):
        """Get current results and update results list"""
        if not self.player_id:
            return
        
        results_response = self.client.get_player_results(self.player_id)
        
        if "error" in results_response:
            self.log_status(f"Error getting current results: {results_response['error']}")
            return
        
        self.results = results_response if isinstance(results_response, list) else []
        
        if self.results:
            latest_result = self.results[-1]  # Get most recent result
            round_num = latest_result.get("roundNumber", "?")
            score = latest_result.get("score", 0)
            answer_correct = latest_result.get("answerCorrect", False)
            move = latest_result.get("move")
            move_name = self.get_move_name(move) if move is not None else "None"
            
            # Check if this is a new round completion
            if round_num > self.last_completed_round:
                self.last_completed_round = round_num
                self.latest_score = score
                self.log_status(f"🎉 Round {round_num} COMPLETED! Score: {score} points, Answer: {'✓' if answer_correct else '✗'}, Move: {move_name}")
                self.log_status(f"✨ +{score} points added to total score!")
            else:
                self.log_status(f"Round {round_num} result: {score} points, Answer: {'✓' if answer_correct else '✗'}, Move: {move_name}")
    
    def get_final_results(self):
        """Get and display final results"""
        if not self.player_id:
            return
        
        self.log_status("Fetching final results...")
        results_response = self.client.get_player_results(self.player_id)
        
        if "error" in results_response:
            self.log_status(f"Error getting results: {results_response['error']}")
            return
        
        self.results = results_response if isinstance(results_response, list) else []
        
        if self.results:
            total_score = sum(result.get("score", 0) for result in self.results)
            self.log_status(f"Final Results - Total Score: {total_score}")
            
            for result in self.results:
                round_num = result.get("roundNumber", "?")
                score = result.get("score", 0)
                answer_correct = result.get("answerCorrect", False)
                move = result.get("move")
                move_name = self.get_move_name(move) if move is not None else "None"
                
                self.log_status(f"Round {round_num}: Score {score}, Answer Correct: {answer_correct}, Move: {move_name}")
        else:
            self.log_status("No results available.")
    
    def start_autonomous_play(self):
        """Start the autonomous game playing in a separate thread"""
        if self.is_running:
            return
        
        game_thread = threading.Thread(target=self.monitor_and_play)
        game_thread.daemon = True
        game_thread.start()
    
    def stop(self):
        """Stop the autonomous game playing"""
        self.is_running = False