from flask import Flask, request, jsonify, render_template
import os
import requests
import sqlite3
import openai
import pyttsx3
import json

# Initialiser l'application Flask
app = Flask(__name__)

# Set OpenAI key
openai.api_key = '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'

# Connect to SQLite database
conn = sqlite3.connect('chat_history.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY,
        user_message TEXT,
        bot_message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Configurer le moteur OpenAI
engine = "davinci-codex"

# Configurer le synthétiseur vocal
engine_speech = pyttsx3.init()

DALLE_API_URL = 'https://api.openai.com/v1/images/dalle'

# Fonction pour appeler l'API OpenAI
def call_openai_api(prompt):
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=50
    )
    return response.choices[0].text.strip()

# Gestion des commandes spéciales
def handle_special_commands(command):
    if command.startswith('/image'):
        prompt = command.replace('/image', '').strip()
        if prompt:
            image_url = generate_image_with_dalle(prompt)
            if image_url:
                response = f'<img src="{image_url}" alt="Generated Image">'
            else:
                response = 'Une erreur s\'est produite lors de la génération de l\'image.'
        else:
            response = 'Veuillez fournir une requête pour générer une image.'
    elif command.startswith('/speech'):
        response = "Commande speech : réponse vocalisée"
        speech_output(response)
    elif command.startswith('/stable-diffusion'):
        response = "Commande stable-diffusion : utilisation des services de stable-diffusion"
    else:
        response = call_openai_api(command)

    return response

# Fonction pour synthétiser la réponse en voix
def speech_output(text):
    engine_speech.say(text)
    engine_speech.runAndWait()

# Fonction pour générer une image avec DALL-E
def generate_image_with_dalle(prompt):
    headers = {
        'Authorization': f'Bearer {openai.api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'prompt': prompt,
        'num_images': 1
    }

    response = requests.post(DALLE_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        image_url = response.json()['output']['images'][0]['resized']
        return image_url
    else:
        return None

# Route pour gérer les entrées de l'utilisateur
@app.route('/user-input', methods=['POST','GET'])
def handle_user_input():
    user_input = request.json['user_input']
    if user_input.startswith('/'):
        response = handle_special_commands(user_input)
    else:
        response = call_openai_api(user_input)
        conn.execute('''
            INSERT INTO chat_history (user_message, bot_message) 
            VALUES (?, ?)
        ''', (user_input, response))
        conn.commit()
    return jsonify({'response': response}), 200, {'Content-Type': 'application/json'}

@app.route('/')
def home():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)
