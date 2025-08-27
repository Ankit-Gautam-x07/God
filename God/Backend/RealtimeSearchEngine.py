from googlesearch import search
from groq import Groq  # Importing the Groq library to use its API.
from json import load, dump # Importing functions to read and write JSON file.
import datetime # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values # Importing dotenv_values to read environment variable from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve specific environment variable for username, assistant name, and API Key.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client with provided API key.
client = Groq(api_key=GroqAPIKey)

# Function to get real-time information like the current date and time.
def Information():
    """
    Get real-time information like the current date and time.
    
    Returns:
        str: Formatted string with current date and time information.
    """
    current_date_time = datetime.datetime.now()     # Get the current date and time.
    day = current_date_time.strftime("%A")      # Day of the week.
    date = current_date_time.strftime("%d")     # Day of the month.
    month = current_date_time.strftime("%B")    # Full month name.
    year = current_date_time.strftime("%Y")     #  Year.
    hour = current_date_time.strftime("%H")     # Hour in 24-hour format.
    minute = current_date_time.strftime("%M")   # Minute.
    second = current_date_time.strftime("%S")   # Second.
    data = f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

# Get real-time information
real_time_info = Information()

# Define the system instructions for the chatbot.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***

Use the following real-time information if needed:
{real_time_info}"""

# Global variable to store chat messages
messages = []

# Function to perform a Google search and format the results.
def GoogleSearch(query):
    """
    Perform a Google search and format the results.
    
    Args:
        query (str): The search query.
        
    Returns:
        str: Formatted search results.
    """
    try:
        results = list(search(query, advanced=True, num_results=5))
        if not results:
            return f"No search results found for '{query}'."
        
        Answer = f"The search results for '{query}' are:\n[start]\n"

        for i in results:
            Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

        Answer += "[end]"
        return Answer
    except Exception as e:
        return f"An error occurred while searching for '{query}': {str(e)}"

# Function to clean up the answer by removing empty lines.
def AnswerModifier(Answer):
    """
    Remove empty lines from the answer to make it more readable.
    
    Args:
        Answer (str): The raw answer string with possible empty lines.
        
    Returns:
        str: The cleaned answer string without empty lines.
    """
    if not Answer:
        return Answer
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# System messages for the chatbot conversation.
SystemChatBot = [
    {"role": "system", "content": System},
]

# Function to get real-time information like the current date and time.
def Information():
    """
    Get real-time information like the current date and time.
    
    Returns:
        str: Formatted string with current date and time information.
    """
    current_date_time = datetime.datetime.now()     # Get the current date and time.
    day = current_date_time.strftime("%A")      # Day of the week.
    date = current_date_time.strftime("%d")     # Day of the month.
    month = current_date_time.strftime("%B")    # Full month name.
    year = current_date_time.strftime("%Y")     #  Year.
    hour = current_date_time.strftime("%H")     # Hour in 24-hour format.
    minute = current_date_time.strftime("%M")   # Minute.
    second = current_date_time.strftime("%S")   # Second.
    data = f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

# Function to handle real-time search and response generation.
def RealtimeSearchEngine(prompt):
    """
    Handle real-time search and response generation.
    
    Args:
        prompt (str): The user's query.
        
    Returns:
        str: The AI's response to the query.
    """
    global SystemChatBot, messages

    try:
        # Load the chat log from the JSON file.
        try:
            with open(r"Data/ChatLog.json", "r") as f:
                messages = load(f)
        except FileNotFoundError:
            messages = []
        messages.append({"role": "user", "content": f"{prompt}"})

        # Add Google search results to the system chatbot messages.
        SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

        # Generate a response using the Groq client.
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )
        
        Answer = ""

        # Concatenate response chunks from the streaming output.
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        # Clean up the response.
        Answer = Answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        # Save the updated chat log back to the JSON file.
        with open(r"Data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        # Remove the most recent system message from the chatbot conversation.
        SystemChatBot.pop()
        return AnswerModifier(Answer=Answer)
    except Exception as e:
        # Remove the most recent system message from the chatbot conversation in case of error.
        if len(SystemChatBot) > 1:  # Only pop if we added a message
            SystemChatBot.pop()
        return f"An error occurred: {str(e)}"

# Main entry point for interactive querying.
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
