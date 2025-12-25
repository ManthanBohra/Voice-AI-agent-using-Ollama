import speech_recognition as sr
import pyttsx3  
import ollama


def listen():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Listening... (Speak now)")
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            # Listen for audio input
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Processing...")

        # Recognize speech using Google's free API
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text

    except sr.WaitTimeoutError:
        print("No speech detected (timeout).")
        return None
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        return None
    except sr.RequestError:
        print("Speech recognition service unavailable.")
        return None
    except Exception as e:
        print(f"An error occurred in listen(): {e}")
        return None
    
def think(text: str):
    if not text:
        return None

    print("Thinking...")

    try:
        # Ensure you have pulled the model via: ollama pull llama3
        response = ollama.chat(
            model="llama3",
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ],
        )

        response_text = response["message"]["content"]
        print(f"AI: {response_text}")
        return response_text

    except Exception as e:
        print(f"An error occurred in think(): {e}")
        return "Sorry, something went wrong while thinking."
    
def speak(text: str):
    if not text:
        return

    try:
        engine = pyttsx3.init()

        # Optional: Change voice properties
        voices = engine.getProperty("voices")
        if voices:
            # Try changing index 0 -> 1 for alternative voice
            engine.setProperty("voice", voices[0].id)

        engine.setProperty("rate", 175)  # Speed of speech

        engine.say(text)
        engine.runAndWait()

    except Exception as e:
        print(f"An error occurred in speak(): {e}")

def main():
    print("--- Voice Assistant Started ---")
    speak("Hello, I am ready. You can start speaking.")

    while True:
        # 1. Listen
        user_input = listen()

        # Skip if nothing heard
        if not user_input:
            continue

        # 2. Check for exit keywords
        if user_input.lower().strip() in ["exit", "stop", "quit"]:
            speak("Goodbye!")
            print("Exiting...")
            break

        # 3. Think
        ai_response = think(user_input)

        # 4. Speak
        speak(ai_response)


if __name__ == "__main__":
    main()