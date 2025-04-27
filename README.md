chat-app/
├── app/
│   ├── routes/
│   │   ├── auth.py
│   │   └── chat.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── chat.html
│   │   ├── login.html
│   │   └── signup.html
│   ├── models.py
│   ├── forms.py
│   ├── socketio_events.py
│   ├── __init__.py
│   ├── extension.py
│   └── static/
├── run.py
├── config.py
├── requirements.txt
└── .env

===========================
# Create a virtual environment (recommended)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

===========================
pip install flask flask-socketio flask-login flask-pymongo python-dotenv gevent
