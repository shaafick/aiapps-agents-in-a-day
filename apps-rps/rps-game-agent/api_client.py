import requests
import json
import logging
import os
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RPSGameClient:
    """Client for communicating with the RPS Game Server API"""
    
    def __init__(self, base_url: str = None, room_id: int = 1):
        if base_url is None:
            base_url = os.getenv("RPS_SERVER_URL", "http://localhost:5289")
        self.base_url = base_url.rstrip('/')
        self.room_id = room_id
        self.session = requests.Session()
    
    def register_player(self, name: str) -> Dict[str, Any]:
        """Register a new player with the server"""
        url = f"{self.base_url}/api/player/register"
        data = {"Name": name, "RoomId": self.room_id}
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def get_player_status(self, player_id: int) -> Dict[str, Any]:
        """Get current tournament status for a player"""
        url = f"{self.base_url}/api/player/{player_id}/status?roomId={self.room_id}"
        logger.info(f"GET {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def submit_answer(self, player_id: int, round_number: int, answer: str, move: int) -> Dict[str, Any]:
        """Submit answer and RPS move for current round"""
        url = f"{self.base_url}/api/player/submit-answer?roomId={self.room_id}"
        data = {
            "PlayerId": player_id,
            "RoundNumber": round_number,
            "Answer": answer,
            "Move": move  # 0=Rock, 1=Paper, 2=Scissors
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(e)
            return {"error": str(e)}
    
    def get_player_results(self, player_id: int) -> Dict[str, Any]:
        """Get all results for a specific player"""
        url = f"{self.base_url}/api/player/{player_id}/results?roomId={self.room_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}