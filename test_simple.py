import asyncio
import websockets
import json

async def test_simple():
    stream_id = "8cb1154e-8e7e-4ac2-8e56-8ebbb22e4dab"
    
    # Test only control connection
    print("Testing control WebSocket only...")
    uri = f"ws://localhost:8000/ws/stream?id={stream_id}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Control WebSocket connected!")
            
            # Send start command
            await websocket.send(json.dumps({"action": "start"}))
            print("Sent start command")
            
            # Listen for messages
            message_count = 0
            while message_count < 10:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    message_count += 1
                    
                    if isinstance(message, bytes):
                        print(f"ERROR: Received binary data on control connection: {len(message)} bytes")
                        break
                    else:
                        print(f"Received text: {message}")
                        
                        if '"type":"video_start"' in message:
                            print("Video start signal received - should not receive binary data after this")
                            # Wait a bit more to see if we get binary data
                            try:
                                next_message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                                if isinstance(next_message, bytes):
                                    print(f"ERROR: Control connection received binary data after video_start: {len(next_message)} bytes")
                                else:
                                    print(f"Received text after video_start: {next_message}")
                            except asyncio.TimeoutError:
                                print("No more messages after video_start (good)")
                            break
                        
                except asyncio.TimeoutError:
                    print("Timeout waiting for message")
                    break
                    
    except Exception as e:
        print(f"Control WebSocket error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple())
