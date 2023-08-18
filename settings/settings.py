from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import dotenv

# cargar variables de entorno
dotenv.load_dotenv()

# variables de entorno
USER = dotenv.get_key(dotenv.find_dotenv(), 'USERNAME')
PASSWORD = dotenv.get_key(dotenv.find_dotenv(), 'PASSWORD')
HOST = dotenv.get_key(dotenv.find_dotenv(), 'HOST')
DATABASE = dotenv.get_key(dotenv.find_dotenv(), 'DATABASE')


app = Flask(__name__)
CORS(app)
app.config['TESTING'] = False
if app.config['TESTING']:
    # Configuración de la base de datos para pruebas
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{USER}:{PASSWORD}@{HOST}/{DATABASE}'



db = SQLAlchemy(app)