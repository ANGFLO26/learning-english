"""
Audio handling functionality for the GUI layer.
"""
import os
from gtts import gTTS
from playsound import playsound
import tempfile
from threading import Lock

class AudioHandler:
    def __init__(self, app):
        self.app = app
        self.tts_lock = Lock()
        self.audio_folder = os.path.join(app.root_path, 'static', 'audio')
        
        # Create audio folder if it doesn't exist
        if not os.path.exists(self.audio_folder):
            os.makedirs(self.audio_folder)
    
    def speak_text(self, text, language='en'):
        """Convert text to speech and play it."""
        with self.tts_lock:
            try:
                # Create a temporary file for the audio
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                temp_filename = temp_file.name
                temp_file.close()

                # Generate speech using gTTS
                tts = gTTS(text=text, lang='en' if language == 'en' else 'vi')
                tts.save(temp_filename)
                
                # Play the audio
                playsound(temp_filename)
                
                # Clean up the temporary file
                os.unlink(temp_filename)
                return True
            except Exception as e:
                print(f"TTS Error: {str(e)}")
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
                return False 