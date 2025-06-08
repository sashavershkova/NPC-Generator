import google.generativeai as genai
import os

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_greetings(character):
    model = genai.GenerativeModel("gemini-1.5-flash")
    input_message = f"I am writing a fantasy RPG video game. I have an npc named {character.name} who is {character.age} years old. They are a {character.occupation} who has a {character.personality} personality. Please generate a Python style list of 10 stock phrases they might use when the main character talks to them. Please return just the list without a variable name and square brackets."
    
    try:
        response = model.generate_content(input_message)
        raw_text = response.text.strip()
    except Exception as err:
        print("Error accessing AI", err)
        return []

    greetings_texts_list = []
    for line in raw_text.split("\n"):
        if line.strip():
            final_line = line.strip().strip('",').strip('"')
            greetings_texts_list.append(final_line)

    return greetings_texts_list