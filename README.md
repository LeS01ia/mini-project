Chatbot basé sur GPT-4



Chatbot basé sur GPT-4
Cette application est une interface de chat simple qui utilise GPT-4 d'OpenAI pour générer des réponses aux messages de l'utilisateur.

# Prérequis

Python 3.10 ou supérieur.
Flask
SQLite3
OpenAI Python client (pour interagir avec l'API GPT-4 d'OpenAI)

# Installation

Clonez ce dépôt sur votre machine locale en utilisant git clone.

Accédez au répertoire du projet avec cd project-dir.

Créez un nouvel environnement virtuel avec Python 3.10 et activez-le 

`python3 -m venv env`
`source env/bin/activate`


installez les dépendances nécessaires avec `pip install -r requirements.txt`.

Vous devez également configurer votre clé API OpenAI. Vous pouvez le faire en configurant une variable d'environnement OPENAI_API_KEY.

# Utilisation

Lancez le serveur Flask en exécutant python main.py. Le serveur commencera à écouter sur http://127.0.0.1:5000.

Ouvrez votre navigateur web et accédez à http://127.0.0.1:5000. Vous devriez voir l'interface de chat.

Tapez votre message dans la zone de texte et appuyez sur "Envoyer". Le bot répondra à votre message et l'affichera dans la zone de chat.
