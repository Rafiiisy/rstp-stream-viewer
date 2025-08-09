import asyncio
import websockets
import json
import sys

async def test_websocket():
    # Test with the first stream ID from the database
    stream_id = "8cb1154e-8e7e-4ac2-8e56-8ebbb22e4dab"  # Use the ID from your logs
    
    # Test control connection
    print("Testing control WebSocket connection...")
    uri = f"ws://localhost:8000/ws/stream?id={stream_id}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Control WebSocket connected!")
            
            # Send start command
            await websocket.send(json.dumps({"action": "start"}))
            print("Sent start command")
            
            # Listen for messages
            for i in range(10):  # Listen for 10 messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"Received: {message}")
                    
                    if '"type":"video_start"' in message:
                        print("Video start signal received!")
                        break
                        
                except asyncio.TimeoutError:
                    print("Timeout waiting for message")
                    break
                    
    except Exception as e:
        print(f"Control WebSocket error: {e}")
    
    # Test video-only connection
    print("\nTesting video-only WebSocket connection...")
    uri_video = f"ws://localhost:8000/ws/stream?id={stream_id}&video_only=true"
    
    try:
        async with websockets.connect(uri_video) as websocket:
            print("Video WebSocket connected!")
            
            # Listen for binary data
            chunk_count = 0
            for i in range(50):  # Listen for 50 chunks
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    if isinstance(message, bytes):
                        chunk_count += 1
                        print(f"Received binary chunk {chunk_count}: {len(message)} bytes")
                        if chunk_count >= 5:  # Stop after 5 chunks
                            break
                    else:
                        print(f"Received text: {message}")
                        
                except asyncio.TimeoutError:
                    print("Timeout waiting for video data")
                    break
                    
    except Exception as e:
        print(f"Video WebSocket error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
