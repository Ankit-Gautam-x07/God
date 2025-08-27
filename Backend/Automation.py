# ==========================================
#           AUTOMATION TOOL (Linux)
# ==========================================

# Import required libraries
import subprocess
import webbrowser
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import requests
import keyboard
import asyncio
import os

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Define user-agent for requests
useragent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'

# Predefined responses
professional_responses = [
    "Your satisfaction is my top priority. Feel free to reach out if you need anything else.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

# List to store chatbot messages
messages = []

# System chatbot initialization
SystemChatBot = [{
    "role": "system",
    "context": f"Hello, I am {os.getenv('USER')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems, etc."
}]

# ------------------------------------------
#   Google Search Function
# ------------------------------------------
def GoogleSearch(Topic):
    search(Topic)
    return True

# ------------------------------------------
#   Generate AI Content
# ------------------------------------------
def Content(Topic):
    def OpenGedit(File):
        subprocess.Popen(["gedit", File])  # Linux text editor

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})

        completion = client.chat.completion.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("Content", "")
    ContentByAI = ContentWriterAI(Topic)

    # Save content file
    os.makedirs("Data", exist_ok=True)
    file_path = f"Data/{Topic.lower().replace(' ', '')}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenGedit(file_path)
    return True

# ------------------------------------------
#   YouTube Search Function
# ------------------------------------------
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

# ------------------------------------------
#   Play YouTube Video
# ------------------------------------------
def PlayYouTube(query):
    playonyt(query)
    return True

# ------------------------------------------
#   Open Application / Website
# ------------------------------------------
def OpenApp(app, sess=requests.session()):
    try:
        # Try opening application using xdg-open (Linux default opener)
        subprocess.Popen(["xdg-open", app])
        return True

    except:
        # If app is not found, search on Google
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print("[red]Failed to retrieve search results.[/red]")
            return None

        html = search_google(app)
        if html:
            link = extract_links(html)[0]
            webbrowser.open(link)

        return True

# ------------------------------------------
#   Close Application
# ------------------------------------------
def CloseApp(app):
    try:
        subprocess.run(["pkill", "-f", app])
        return True
    except:
        return False

# ------------------------------------------
#   System-Level Commands (Volume etc.)
# ------------------------------------------
def System(command):
    def mute():
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"])

    def unmute():
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"])

    def volume_up():
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"])

    def volume_down():
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"])

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True

# ------------------------------------------
#   Translate & Execute Commands
# ------------------------------------------
async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith("open "):
            fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
            funcs.append(fun)

        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYouTube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"[yellow]No function found for: {command}[/yellow]")

    results = await asyncio.gather(*funcs)

    for result in results:
        yield result

# ------------------------------------------
#   Automation Runner
# ------------------------------------------
async def Automation(commands: list[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True
