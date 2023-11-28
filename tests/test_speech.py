# BEGIN: 3f8a1b6d8c2c
import unittest
import speech_recognition as sr
from speech import recognize_speech

class TestSpeechRecognition(unittest.TestCase):
    
    def test_speech_recognition(self):
        # create a recognizer object
        r = sr.Recognizer()

        # use the default microphone as the audio source
        with sr.Microphone() as source:
            print("Say something!")
            # listen for audio and store it in audio_data variable
            audio_data = r.record(source, duration=5)
            print("Processing...")

        # recognize speech using Google Speech Recognition
        try:
            text = recognize_speech(audio_data)
            self.assertIsNotNone(text)
            print(f"You said: {text}")
        except sr.UnknownValueError:
            print("Sorry, I could not understand what you said.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
    
if __name__ == '__main__':
    unittest.main()
# END: 3f8a1b6d8c2c

