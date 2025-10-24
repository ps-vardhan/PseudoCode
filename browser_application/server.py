#!/usr/bin/env python3
"""
Concode WebSocket Server for Speech-to-Text
Combines the server functionality from example_browserclient2 with improved error handling
"""

if __name__ == '__main__':
    print("Starting Concode Speech-to-Text Server...")
    
    import sys
    import os
    import asyncio
    import websockets
    import threading
    import numpy as np
    from scipy.signal import resample
    import json
    import logging
    from pathlib import Path

    # Add the audio-to-text directory to the path
    ROOT = Path(__file__).resolve().parent.parent
    AUDIO_DIR = ROOT / "audio-to-text"
    if str(AUDIO_DIR) not in sys.path:
        sys.path.insert(0, str(AUDIO_DIR))

    try:
        from speech_to_text import AudioToTextRecorder
    except ImportError as e:
        print(f"Error importing speech_to_text: {e}")
        print("Please ensure the audio-to-text module is properly installed.")
        sys.exit(1)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('server.log')
        ]
    )
    
    # Reduce websockets logging noise
    logging.getLogger('websockets').setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    # Global state
    is_running = True
    recorder = None
    recorder_ready = threading.Event()
    client_websocket = None
    main_loop = None
    connected_clients = set()

    async def broadcast_to_clients(message):
        """Send message to all connected clients"""
        if connected_clients:
            disconnected = set()
            for websocket in connected_clients.copy():
                try:
                    await websocket.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(websocket)
                except Exception as e:
                    logger.error(f"Error sending to client: {e}")
                    disconnected.add(websocket)
            
            # Remove disconnected clients
            connected_clients -= disconnected

    def on_realtime_text(text):
        """Callback for realtime transcription updates"""
        if main_loop is not None:
            asyncio.run_coroutine_threadsafe(
                broadcast_to_clients(json.dumps({
                    'type': 'realtime',
                    'text': text
                })), main_loop)
        print(f"\rRealtime: {text}", flush=True, end='')

    def on_full_sentence(text):
        """Callback for completed sentences"""
        if main_loop is not None:
            asyncio.run_coroutine_threadsafe(
                broadcast_to_clients(json.dumps({
                    'type': 'fullSentence',
                    'text': text
                })), main_loop)
        print(f"\nSentence: {text}")

    # Recorder configuration
    recorder_config = {
        'spinner': False,
        'use_microphone': False,
        'model': 'large-v2',
        'language': 'en',
        'silero_sensitivity': 0.4,
        'webrtc_sensitivity': 2,
        'post_speech_silence_duration': 0.7,
        'min_length_of_recording': 0,
        'min_gap_between_recordings': 0,
        'enable_realtime_transcription': True,
        'realtime_processing_pause': 0,
        'realtime_model_type': 'tiny.en',
        'on_realtime_transcription_stabilized': on_realtime_text,
    }

    def run_recorder():
        """Initialize and run the speech-to-text recorder"""
        global recorder, is_running
        
        try:
            logger.info("Initializing Speech-to-Text recorder...")
            recorder = AudioToTextRecorder(**recorder_config)
            logger.info("Speech-to-Text recorder initialized successfully")
            recorder_ready.set()

            # Main recorder loop
            while is_running:
                try:
                    full_sentence = recorder.text()
                    if full_sentence:
                        on_full_sentence(full_sentence)
                except Exception as e:
                    logger.error(f"Error in recorder loop: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to initialize recorder: {e}")
            recorder_ready.set()  # Set event even on failure to prevent hanging

    def decode_and_resample(audio_data, original_sample_rate, target_sample_rate=16000):
        """Decode and resample audio data to target sample rate"""
        try:
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            if len(audio_np) == 0:
                return audio_data
                
            num_original_samples = len(audio_np)
            num_target_samples = int(num_original_samples * target_sample_rate / original_sample_rate)
            
            if num_target_samples <= 0:
                return audio_data
                
            resampled_audio = resample(audio_np, num_target_samples)
            return resampled_audio.astype(np.int16).tobytes()
        except Exception as e:
            logger.error(f"Error in resampling: {e}")
            return audio_data

    async def handle_client(websocket, path):
        """Handle WebSocket client connections"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"Client connected: {client_id}")
        connected_clients.add(websocket)

        try:
            async for message in websocket:
                if not recorder_ready.is_set():
                    logger.warning("Recorder not ready, ignoring audio data")
                    continue

                if not recorder:
                    logger.warning("Recorder not initialized, ignoring audio data")
                    continue

                try:
                    # Parse the message format: [metadata_length][metadata][audio_data]
                    if len(message) < 4:
                        continue
                        
                    # Read metadata length (first 4 bytes)
                    metadata_length = int.from_bytes(message[:4], byteorder='little')
                    
                    if len(message) < 4 + metadata_length:
                        continue
                        
                    # Extract metadata
                    metadata_json = message[4:4+metadata_length].decode('utf-8')
                    metadata = json.loads(metadata_json)
                    sample_rate = metadata.get('sampleRate', 16000)
                    
                    # Extract audio chunk
                    audio_chunk = message[4+metadata_length:]
                    
                    if len(audio_chunk) > 0:
                        # Resample if necessary
                        if sample_rate != 16000:
                            resampled_chunk = decode_and_resample(audio_chunk, sample_rate, 16000)
                        else:
                            resampled_chunk = audio_chunk
                            
                        # Feed to recorder
                        recorder.feed_audio(resampled_chunk)
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in metadata: {e}")
                except Exception as e:
                    logger.error(f"Error processing audio message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            connected_clients.discard(websocket)

    async def main():
        """Main server function"""
        global main_loop, is_running
        
        main_loop = asyncio.get_running_loop()

        # Start recorder in separate thread
        recorder_thread = threading.Thread(target=run_recorder, daemon=True)
        recorder_thread.start()
        
        # Wait for recorder to be ready
        logger.info("Waiting for recorder initialization...")
        recorder_ready.wait(timeout=30)  # 30 second timeout
        
        if not recorder_ready.is_set():
            logger.error("Recorder initialization timed out")
            return
            
        if not recorder:
            logger.error("Recorder failed to initialize")
            return

        # Start WebSocket server
        logger.info("Starting WebSocket server on localhost:8001")
        server = await websockets.serve(handle_client, "localhost", 8001)
        
        logger.info("Server ready! Open browser_application/index.html in your browser.")
        logger.info("Press Ctrl+C to stop the server.")
        
        try:
            await server.wait_closed()
        except asyncio.CancelledError:
            logger.info("Server shutdown requested")

    # Main execution
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        is_running = False
        if recorder:
            try:
                recorder.stop()
                recorder.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down recorder: {e}")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("Server stopped")