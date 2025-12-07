import os
from datetime import datetime

class TranscriptManager:
    def __init__(self, output_dir=r"d:\PseudoCode\output\transcript"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_transcript(self, text: str, session_start_time: str):
        """
        Appends the transcribed text to a file named after the session start time.
        
        Args:
            text: The transcribed text to save.
            session_start_time: The timestamp string representing when the session started.
                                Should be a valid filename (e.g. "YYYY-MM-DD_HH-MM-SS").
        """
        if not text:
            return

        filename = f"{session_start_time}.txt"
        file_path = os.path.join(self.output_dir, filename)
        
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"{text}\n")
        except Exception as e:
            print(f"Error saving transcript: {e}")
