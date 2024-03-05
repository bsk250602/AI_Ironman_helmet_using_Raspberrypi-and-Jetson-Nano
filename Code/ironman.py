import Jetson.GPIO as GPIO
import time
import openai
import pyttsx3
import speech_recognition as sr

# Set OpenAI API key
openai.api_key = "Replace with API Key"

# Text-to-speech initialization
engine = pyttsx3.init()

# Speech recognition initialization
recognizer = sr.Recognizer()

# GPIO setup
servo1_pin = 17  # GPIO pin for servo 1
servo2_pin = 15  # GPIO pin for servo 2
led_pin = 19     # GPIO pin for LED

GPIO.setmode(GPIO.BCM)
GPIO.setup(servo1_pin, GPIO.OUT)
GPIO.setup(servo2_pin, GPIO.OUT)
GPIO.setup(led_pin, GPIO.OUT)

# Servo PWM setup
servo1_pwm = GPIO.PWM(servo1_pin, 50)  # 50 Hz frequency
servo2_pwm = GPIO.PWM(servo2_pin, 50)

servo1_pwm.start(0)  # Start at the middle position
servo2_pwm.start(0)  # Start at the middle position

def rotate_servos(angle1, angle2):
    servo1_pwm = None
    servo2_pwm = None

    try:
        # Initialize the PWM objects and start them
        servo1_pwm = GPIO.PWM(servo1_pin, 50)
        servo2_pwm = GPIO.PWM(servo2_pin, 50)
        servo1_pwm.start(0)
        servo2_pwm.start(0)

        duty_cycle1 = angle1 / 18.0 + 2.5
        duty_cycle2 = angle2 / 18.0 + 2.5

        servo1_pwm.ChangeDutyCycle(duty_cycle1)
        servo2_pwm.ChangeDutyCycle(duty_cycle2)

        time.sleep(2)

    except Exception as e:
        print(f"Error in rotate_servos: {e}")

    finally:
        # Stop PWM signals and clean up GPIO
        if servo1_pwm:
            servo1_pwm.stop()
        if servo2_pwm:
            servo2_pwm.stop()

def get_audio():
    try:
        with sr.Microphone() as source:
            print("Speak something:")
            audio_data = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio_data)
            return text.lower()

    except sr.UnknownValueError:
        print("Speech recognition could not understand audio.")
        return ""

    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

try:
    while True:
        input_text = get_audio()

        if input_text:
            print("User: ", input_text)

            if "open" in input_text:
                rotate_servos(0, 0)
                GPIO.output(led_pin, GPIO.HIGH)  # Turn off LED
            elif "close" in input_text:
                rotate_servos(90, 90)
                GPIO.output(led_pin, GPIO.LOW)  # Turn on LED
            else:
                # Make OpenAI API call
                response = openai.ChatCompletion.create(
                    model="gpt-4-1106-preview",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": input_text}
                    ]
                )

                if 'choices' in response and response['choices']:
                    op = response['choices'][0]['message']['content'].strip()
                    print("Assistant: ", op)

                    # Convert OpenAI's response to speech
                    engine.say(op)
                    engine.runAndWait()

except KeyboardInterrupt:
    print("Exiting program...")

finally:
    # Clean up GPIO resources
    GPIO.cleanup()
