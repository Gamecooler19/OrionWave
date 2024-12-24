import asyncio
import websockets
import json
from typing import Dict, Any
import logging
import socket
from ..types import VoiceProcessorProtocol

logger = logging.getLogger(__name__)

class VoiceChangerServer:
    def __init__(self, processor: VoiceProcessorProtocol, host: str = 'localhost', start_port: int = 8765):
        self.processor = processor
        self.host = host
        self.port = self._find_available_port(start_port)
        self.clients = set()
        
    def _find_available_port(self, start_port: int, max_tries: int = 10) -> int:
        """Find first available port starting from start_port"""
        for port in range(start_port, start_port + max_tries):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind((self.host, port))
                    return port
                except OSError:
                    continue
        raise RuntimeError("No available ports found")

    async def start(self):
        try:
            async with websockets.serve(self.handle_client, self.host, self.port):
                logger.info(f"WebSocket server running on ws://{self.host}:{self.port}")
                await asyncio.Future()  # run forever
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            # Don't raise, allow program to continue without server
            return

    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        self.clients.add(websocket)
        try:
            async for message in websocket:
                await self.process_command(websocket, message)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.clients.remove(websocket)

    async def process_command(self, websocket, message):
        """Process incoming commands"""
        try:
            data = json.loads(message)
            command = data.get('command')
            params = data.get('params', {})

            if command == 'add_effect':
                self.processor.add_effect(params['name'], params.get('settings'))
                await self.broadcast_status()

            elif command == 'load_preset':
                self.processor.load_preset(params['name'])
                await self.broadcast_status()

            elif command == 'get_stats':
                await websocket.send(json.dumps({
                    'type': 'stats',
                    'data': self.processor.get_audio_stats()
                }))

        except Exception as e:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def broadcast_status(self):
        """Broadcast current status to all clients"""
        status = {
            'type': 'status',
            'data': {
                'effects': self.processor.effects_chain,
                'active_preset': self.processor.preset_manager.current_preset,
                'voice_active': self.processor.voice_active
            }
        }
        message = json.dumps(status)
        for client in self.clients:
            try:
                await client.send(message)
            except:
                pass
