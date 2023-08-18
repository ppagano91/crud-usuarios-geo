from settings.settings import db
from sqlalchemy import create_engine, text, event
from helpers.md5 import md5
import dotenv

dotenv.load_dotenv()

USER = dotenv.get_key(dotenv.find_dotenv(), 'USERNAME')
PASSWORD = dotenv.get_key(dotenv.find_dotenv(), 'PASSWORD')
HOST = dotenv.get_key(dotenv.find_dotenv(), 'HOST')
DATABASE = dotenv.get_key(dotenv.find_dotenv(), 'DATABASE')

engine=create_engine(f'postgresql://{USER}:{PASSWORD}@{HOST}/{DATABASE}')

class Usuario(db.Model):
    __tablename__ = 'se_usuario'
    __table_args__ = {'schema': 'geositm',
                        'extend_existing': True,
                        'autoload_with': engine
                    }
    
    registros = db.relationship('UsuarioRegistro', backref='usuario', lazy="select", cascade='all, delete-orphan')

    def registrar_usuario(self, registro, fecha_de_operacion, usuario_operacion):       

        # query = text("SELECT md5(:argumento) AS resultado")
        # resultado = db.session.execute(query, {"argumento": registro}).fetchone()

        nuevo_registro = UsuarioRegistro(
            id_usuario=self.id_usuario,
            registro=md5(registro),
            fecha_operacion=fecha_de_operacion,
            usuario_operacion=usuario_operacion
        )
        db.session.add(nuevo_registro)
        db.session.commit()

    

class UsuarioRegistro(db.Model):
    __tablename__ = 'se_usuario_registro'
    __table_args__ = {'schema': 'geositm',
                        'extend_existing': True,
                        'autoload_with': engine
                    }

    id_usuario = db.Column(db.Integer, db.ForeignKey('geositm.se_usuario.id_usuario'))
    
