import speech_recognition as sr
import numpy as np

# create a recognizer object
r = sr.Recognizer()

keyword = 'Jarvis'

# use the default microphone as the audio source
while True:
    input("Press enter to continue...")
    
    with sr.Microphone() as source:
        # listen for audio and store it in audio_data variable
        audio_data = r.listen(source)
        print("Processing...")




    # recognize speech using Google Speech Recognition
    try:
        text = r.recognize_whisper(audio_data)
        #text = r.recognize_google(audio_data, language='sv-SE')
        print(f"You said: {text}")
        
    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

