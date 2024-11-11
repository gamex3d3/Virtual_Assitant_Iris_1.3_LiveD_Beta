import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import JarvisAI
import sys
from urllib.request import urlopen
import pprint
import pyautogui
import json
import configparser
import wolframalpha
import wikipedia
import os
import random
from transformers import MarianMTModel, MarianTokenizer
import winsound
import torch
import time
from plyer import notification
import spacy
import cv2
import face_recognition
import numpy as np
from time import sleep
import dlib
import face_recognition as fr
from gtts import gTTS

# Initialize recognizer, text-to-speech engine, and NLP model
listener = sr.Recognizer()
machine = pyttsx3.init()
obj = JarvisAI.JarvisAssistant()
nlp = spacy.load('en_core_web_sm')

# Set voice properties
voices = machine.getProperty("voices")
machine.setProperty("voice", voices[1].id)

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

def talk(text):
    machine.say(text)
    machine.runAndWait()

def print_and_talk(text):
    print(text)
    talk(text)

def input_instruction():
    try:
        with sr.Microphone() as origin:
            print_and_talk("Hi, How can I help sir?...")
            speech = listener.listen(origin)
            instruction = listener.recognize_google(speech).lower()
            return instruction
    except sr.UnknownValueError:
        return ""

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 0.5
        r.energy_threshold = 300

app_id = "7E8RXT-79EJLE6LUQ"
def computational_intelligence(question):
    try:
        client = wolframalpha.Client(app_id)
        answer = client.query(question)
        return next(answer.results).text
    except Exception:
        talk("Sorry sir! Please can you repeat.")
        return None

def set_alarm(alarm_time):
    try:
        alarm_hour, alarm_minute = map(int, alarm_time.split(':'))
        while True:
            current_time = time.localtime()
            if current_time.tm_hour == alarm_hour and current_time.tm_min == alarm_minute:
                print("Time's up!")
                winsound.Beep(1000, 3000)
                break
            time.sleep(60)
    except ValueError:
        print("Invalid time format. Please use HH:MM.")

def set_reminder(reminder_text, reminder_time):
    try:
        reminder_time = datetime.datetime.strptime(reminder_time, '%Y-%m-%d %H:%M')
        time_diff = (reminder_time - datetime.datetime.now()).total_seconds()
        if time_diff <= 0:
            print("The reminder time should be in the future.")
            return
        time.sleep(time_diff)
        notification.notify(
            title='Reminder',
            message=reminder_text,
            app_name='Iris 1.3',
            timeout=10
        )
    except ValueError:
        print("Invalid date/time format. Please use 'YYYY-MM-DD HH:MM' format.")

def translate_text(input_text, source_lang, target_lang, max_length=50):
    model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{target_lang}'
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    with torch.no_grad():
        translated_ids = model.generate(input_ids, max_length=max_length)
    return tokenizer.decode(translated_ids[0], skip_special_tokens=True, max_length=max_length)

def play_iris():
    while True:
        instruction = input_instruction()
        if not instruction:
            continue

        print(instruction)
        if "play" in instruction:
            song = instruction.replace('play', "").strip()
            talk(f"Ok sir, I'm playing {song}")
            pywhatkit.playonyt(song)

        elif "location" in instruction or "where am i" in instruction:
            url = 'http://ipinfo.io/json'
            data = json.load(urlopen(url))
            print(data)
            talk(data)

        elif "search" in instruction or "where is" in instruction:
            query = instruction.replace("search", "").strip()
            summary = wikipedia.summary(query, sentences=3)
            print_and_talk(summary)

        elif "google" in instruction:
            query = instruction.replace("google", "").strip()
            pywhatkit.search(query)

        elif 'who is' in instruction:
            person = instruction.replace('who is', "").strip()
            info = wikipedia.summary(person, 1)
            print_and_talk(info)

        elif "everything on" in instruction:
            topic = instruction.replace("everything on", "").strip()
            talk(f"Here is everything on {topic}")
            results = wikipedia.search(topic)
            print_and_talk(results)

        elif "alarm" in instruction or "set an alarm" in instruction:
            talk("Setting an alarm sir!")
            alarm_time = input("Enter the alarm time (HH:MM): ")
            set_alarm(alarm_time)

        elif "reminder" in instruction:
            talk("Setting a reminder sir!")
            reminder_text = instruction.replace("set a reminder", "").strip()
            reminder_time = input("Enter the reminder date and time (YYYY-MM-DD HH:MM): ")
            set_reminder(reminder_text, reminder_time)

        elif "weather" in instruction or "forecast" in instruction:
            city = instruction.split()[-1]
            weather_res = obj.weather(city=city)
            print_and_talk(weather_res)

        elif "timer for" in instruction:
            timer_duration = int(instruction.replace('timer for', "").strip())
            talk(f"Setting a timer for {timer_duration} seconds sir!")
            for x in range(timer_duration, 0, -1):
                seconds = x % 60
                minutes = (x // 60) % 60
                hours = x // 3600
                print(f"{hours:02}:{minutes:02}:{seconds:02}")
                time.sleep(1)
            print_and_talk("Time's Up Sir!")

        elif "date" in instruction or "the time" in instruction:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            print_and_talk(f"Today's date is {current_date}, sir")
            print_and_talk(f"The time right now is {current_time}, sir")

        elif "calculate" in instruction or "what is" in instruction or "how many" in instruction:
            answer = computational_intelligence(instruction)
            if answer:
                print_and_talk(answer)

        elif "note" in instruction:
            talk("What would you like me to write down?")
            note_text = obj.mic_input()
            with open("default.txt", 'w') as f:
                f.write(note_text)
            talk(f"I successfully created the note: {note_text}")

        elif "wait" in instruction:
            if "10 seconds" in instruction:
                time.sleep(10)
            elif "30 seconds" in instruction:
                time.sleep(30)
            elif "1 minutes" in instruction:
                time.sleep(60)
            else:
                time.sleep(60)

        elif "favourite playlist" in instruction or "music folder" in instruction:
            music_folder = "c:\\Musics\\"
            music = ("music1", "music2", "music3", "music4", "music5", "music6")
            random_music = os.path.join(music_folder, f"{random.choice(music)}.mp3")
            os.system(random_music)
            talk("Playing your playlist sir!!")

        elif "translate" in instruction:
            input_text = instruction.replace('translate', "").strip()
            source_lang = "en"
            if 'french' in instruction:
                target_lang = "fr"
            elif 'spanish' in instruction:
                target_lang = "es"
            elif 'german' in instruction:
                target_lang = "de"
            else:
                talk("language not known!")
            translated_text = translate_text(input_text, source_lang, target_lang, max_length=100)
            print_and_talk(f"Translated: {translated_text}")

        elif "news" in instruction:
            news_res = obj.news()
            if "continue" in instruction:
                talk(news_res)
            else:
                pprint.pprint(news_res)
                talk(f"I have found {len(news_res)} news articles sir. Let me tell you the first two of them.")
                talk(news_res[0])
                talk(news_res[1])

        elif "screenshot" in instruction:
            talk("By what name do you want to save the screenshot?")
            name = obj.mic_input().strip()
            talk("Alright sir, taking the screenshot")
            img = pyautogui.screenshot()
            img.save(f"{name}.png")
            talk("The screenshot has been successfully captured")

        elif "open" in instruction:
            app_name = instruction.split(' ', 1)[1].strip()
            dict_app = {
                'chrome': 'C:\\Program Files\\Google\\Chrome\\Application\\chrome_proxy.exe',
                'a r': 'C:\\Program Files\\Adobe\\Adobe Aero 2022 (Beta)\\Aero.exe',
                'blender': 'C:\\Program Files\\Blender Foundation\\Blender 3.4\\Blender-launcher.exe',
                'meshroom': 'C:\\Users\\ABC\\Downloads\\Meshroom-2023.2.0-win64\\Meshroom-2023.2.0\\Meshroom.exe'
            }
            path = dict_app.get(app_name)
            if path:
                talk(f'Launching: {app_name}')
                obj.launch_any_app(path_of_app=path)
            else:
                print_and_talk('Application path not found')

        elif "save conversation" in instruction:
            machine.save_to_file(text=instruction, filename='convo.mp3')
            machine.runAndWait()

        elif "thank you" in instruction or "that's all" in instruction or "that is all" in instruction:
            talk("Okay. Bye Sir, have a good day.")
            sys.exit()

        else:
            talk("I don't understand you sir!")

if __name__ == "__main__":
    play_iris()
