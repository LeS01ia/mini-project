from flask import Flask, request, jsonify, render_template
import requests
import sqlite3
import openai
import pyttsx3
import traceback
import base64
import threading

import json


# Initialize the Flask app
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

# Configure the OpenAI engine for ChatGPT-3
chatgpt3_engine = "gpt-3.5-turbo"

# Configure the speech synthesizer
engine_speech = pyttsx3.init()

# Configure DALL-E API URL
dalle_api_url = 'https://api.openai.com/v1/images/generations'

# Function to call the OpenAI API
def call_openai_api(prompt):
    response = openai.ChatCompletion.create(
        model=chatgpt3_engine,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# Function to synthesize the response into voice

# Créez un verrou
lock = threading.Lock()


# Créez un verrou
lock = threading.Lock()

# Initialisez le moteur de synthèse vocale
engine_speech = pyttsx3.init()

def speech_output(text):
    # Obtenez le verrou
    with lock:
        try:
            engine_speech.say(text)
            engine_speech.runAndWait()
        finally:
            engine_speech.stop()





# Function to call the DALL-E API and generate an image
def generate_image_with_dalle(prompt):
    headers = {
        'Authorization': f'Bearer {openai.api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'prompt': prompt,
        'n': 1,
        'size': '256x256'
    }

    response = requests.post(dalle_api_url, headers=headers, json=data)
    if response.status_code == 200:
        image_data = response.json()
        return image_data
    else:
        return None

# Handle special commands
def handle_special_commands(command):
    if command.startswith('/image'):
        prompt = command.replace('/image', '').strip()
        if prompt:
            image_data = generate_image_with_dalle(prompt)
            if image_data and 'data' in image_data:
                response = 'Voici une image générée :'
                image_urls = [img['url'] for img in image_data['data']]  # Extract URLs from the response data
                return response, image_urls
            else:
                response = 'Une erreur s\'est produite lors de la génération de l\'image.'
                return response, None

    # Retourne uniquement la réponse en cas de requête vide
    elif command.startswith('/speech'):
        text = command.replace('/speech', '').strip()
        if text:
            response = f"Commande speech : {text}"
            speech_output(text)  # Ajouter cette ligne pour vocaliser le texte
        else:
            response = 'Veuillez fournir du texte pour la commande speech.'
        return response, None  # Retourne uniquement la réponse pour la commande speech
    elif command.startswith('/stable-diffusion'):
        response = "Commande stable-diffusion : utilisation des services de stable-diffusion"
        return response, None  # Retourne uniquement la réponse pour la commande stable-diffusion
    else:
        response = call_openai_api(command)
        return response, None  # Retourne uniquement la réponse pour les autres commandes

# Route to handle user input
@app.route('/user-input', methods=['POST'])
def handle_user_input():
    # Connect to SQLite database
    conn = sqlite3.connect('chat_history.db')

    try:
        user_input = request.json['user_input']
        image_urls = None  # Initialize image_urls to None

        if user_input.startswith('/'):
            response, image_urls = handle_special_commands(user_input)
            if image_urls:
                image_data_base64 = [base64.b64encode(requests.get(url).content).decode('utf-8') for url in image_urls]  # Convertit les données binaires en base64
                image_urls = [f"data:image/jpeg;base64,{image}" for image in image_data_base64]  # Génère les URLs des images base64

        else:
            response = call_openai_api(user_input)
            conn.execute('''
                INSERT INTO chat_history (user_message, bot_message) 
                VALUES (?, ?)
            ''', (user_input, response))
            conn.commit()
    except Exception as e:
        # Handle exceptions and return an error response
        print("Error:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the database connection
        conn.close()

    return jsonify({'response': response, 'image_urls': image_urls}), 200


@app.route('/')
def home():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)
