"""
Run All - Orchestrates Game Tools Agent Server and Client
=========================================================
Starts the game tools agent server and then the client

Prerequisites:
    pip install -r requirements.txt

Usage:
    python main.py
"""

import asyncio
import subprocess
import sys
import time
import signal
import httpx
import os
import threading
from dotenv import load_dotenv

load_dotenv()

server_url = os.environ.get("SERVER_URL", "localhost")
game_tools_port = os.environ.get("GAME_TOOLS_AGENT_PORT", "8088")

servers = [
    {
        "name": "game_tools_agent_server",
        "module": "game_tools_agent.server:app",
        "port": game_tools_port
    }
]

server_procs = []


async def wait_for_server_ready(server, timeout=30):
    """Wait for server to be ready by checking health endpoint"""
    async with httpx.AsyncClient() as client:
        start = time.time()
        while True:
            try:
                health_url = f"http://{server_url}:{server['port']}/health"
                r = await client.get(health_url, timeout=2)
                if r.status_code == 200:
                    print(f"✅ {server['name']} is healthy and ready!")
                    return True
            except Exception:
                pass
            if time.time() - start > timeout:
                print(f"❌ Timeout waiting for server health at {health_url}")
                return False
            await asyncio.sleep(1)


def stream_subprocess_output(process):
    """Stream subprocess output to console"""
    while True:
        line = process.stdout.readline()
        if not line:
            break
        print(line.rstrip())


async def run_game_agent_main():
    """Import and run the game agent main function"""
    from game_agent import main as game_agent_main
    await game_agent_main()


async def main():
    print("=" * 60)
    print("🚀 Starting Game Agent A2A System")
    print("=" * 60)
    print()
    
    # Start server subprocesses
    print("🚀 Starting server subprocesses...")
    for server in servers:
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            server["module"],
            "--host",
            server_url,
            "--port",
            str(server["port"]),
            "--log-level",
            "info"
        ]
        
        print(f"🚀 Starting {server['name']} on port {server['port']}")
        process = subprocess.Popen(
            cmd,
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True,
        )
        server_procs.append(process)

        thread = threading.Thread(target=stream_subprocess_output, args=(process,), daemon=True)
        thread.start()

        ready = await wait_for_server_ready(server)
        if not ready:
            print(f"❌ Server '{server['name']}' failed to start, killing process...")
            process.kill()
            sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ All servers are ready!")
    print("=" * 60)
    print()
    
    # Run the game agent client
    try:
        await run_game_agent_main()
    except Exception as e:
        print(f"❌ Game Agent stopped: {e}")
    finally:
        print()
        print("=" * 60)
        print("🛑 Stopping server subprocesses...")
        print("=" * 60)
        
        # Terminate the server subprocess gracefully
        for process in server_procs:
            if process.poll() is None:  # Still running
                if sys.platform == "win32":
                    process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("✅ All servers stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 System stopped by user")
        # Cleanup
        for process in server_procs:
            if process.poll() is None:
                process.terminate()
