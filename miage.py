from flask import Flask, request, jsonify, render_template
import requests
import sqlite3
import openai
import pyttsx3

# Initialize the Flask app
app = Flask(__name__)

# Set OpenAI key
openai.api_key = 'api'

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
def speech_output(text):
    engine_speech.say(text)
    engine_speech.runAndWait()

# Function to call the DALL-E API and generate an image
def generate_image_with_dalle(prompt):
    headers = {
        'Authorization': f'Bearer {openai.api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'description': prompt,
        'image': None
    }

    response = requests.post(dalle_api_url, headers=headers, json=data)
    if response.status_code == 200:
        image_url = response.json()['output']['url']
        return image_url
    else:
        return None

# Route to handle user input
@app.route('/user-input', methods=['POST'])
def handle_user_input():
    # Connect to SQLite database
    conn = sqlite3.connect('chat_history.db')

    try:
        user_input = request.json['user_input']
        image_url = None  # Initialize image_url to None

        if user_input.startswith('/'):
            response, image_url = handle_special_commands(user_input)
        else:
            response = call_openai_api(user_input)
            conn.execute('''
                INSERT INTO chat_history (user_message, bot_message) 
                VALUES (?, ?)
            ''', (user_input, response))
            conn.commit()
    except Exception as e:
        # Handle exceptions and return an error response
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the database connection
        conn.close()

    return jsonify({'response': response, 'image_url': image_url}), 200

# Handle special commands
def handle_special_commands(command):
    image_url = None
    if command.startswith('/image'):
        prompt = command.replace('/image', '').strip()
        if prompt:
            image_url = generate_image_with_dalle(prompt)
            if image_url:
                response = 'Voici une image générée :'
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

    return response, image_url

@app.route('/')
def home():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)
