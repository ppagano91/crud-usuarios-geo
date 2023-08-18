from flask import Flask, request, jsonify
from settings.settings import app
from models.models import Usuario, UsuarioRegistro
from settings.settings import db
import re
import datetime
from helpers.md5 import md5


@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'It works!'})

@app.route('/usuarios', methods=['GET'])
def get_usuarios():    
    usuarios = Usuario.query.options(db.joinedload(Usuario.registros)).all()
    
    output = []
    usuario_data = {}
    for usuario in usuarios:
        print(usuario.registros)
        usuario_data = {}
        usuario_data['id'] = usuario.id_usuario
        usuario_data['nombre'] = usuario.nombre
        usuario_data['nro_doc'] = usuario.nro_doc
        usuario_data['mail'] = usuario.mail

        # for registro in usuario.registros:
        #     registro_data = {
        #         'id_registro': registro.id_usuario_registro,
        #         'password': registro.registro,
        #         'fecha_operacion': registro.fecha_operacion,
        #         'usuario_operacion': registro.usuario_operacion
        #     }
        #     usuario_data['registros']=registro_data

        output.append(usuario_data)
    return jsonify({'usuarios': output})


# Obtener un usuario por id
@app.route('/usuarios/<id>', methods=['GET'])
def get_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({'message': 'No se encontro el usuario'})
    usuario_data = {}
    usuario_data['id'] = usuario.id_usuario
    usuario_data['nombre'] = usuario.nombre
    usuario_data['nro_doc'] = usuario.nro_doc
    usuario_data['mail'] = usuario.mail

    return jsonify({'usuario': usuario_data})

# Crear usuario
@app.route('/usuarios', methods=['POST'])
def create_usuario():
    try:
        data = request.get_json()

        # Validar que ninguno de los campos esté vacío
        if not data['nombre'] or not data['nro_doc'] or not data['login'] or not data['mail'] or not data['password']:
            return jsonify({'message': 'Todos los campos son obligatorios'})

        # Validar que el usuario por nro_doc y por login no exista
        usuario = Usuario.query.filter_by(nro_doc=data['nro_doc']).first()
        print(usuario)
        if usuario:
            return jsonify({'message': 'Ya existe un usuario con ese nro_doc'})
        
        usuario = Usuario.query.filter_by(login=data['login']).first()
        if usuario:
            return jsonify({'message': 'Ya existe un usuario con ese login'})
        
        # Validar el formato del email con expresiones regulares
        # Validar que el email no exista.
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data["mail"]):
            return jsonify({'message': 'El mail tiene un formato inválido'})
        
        # Validar que el password tenga al menos 8 caracteres
        if len(data['password']) < 8:
            return jsonify({'message': 'El password debe tener al menos 8 caracteres'})
            
        # Validar que el password tenga al menos una letra mayúscula, una minúscula y un número
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$', data["password"]):
            return jsonify({'message': 'El password debe tener al menos una letra mayúscula, una minúscula y un número'})

        # Crear el usuario
        fecha_alta= datetime.datetime.now()
        nuevo_usuario = Usuario(nombre=data['nombre'],apellido=data['apellido'],id_tipo_doc=data["id_tipo_doc"], nro_doc=data['nro_doc'], login=data['login'], mail=data['mail'], fecha_alta=fecha_alta,fecha_modificacion=fecha_alta, id_sector=data["id_sector"],habilitado=False,usuario_alta=2,usuario_modificacion=2)
        db.session.add(nuevo_usuario)
        db.session.commit()

        # Crear el registro
        nuevo_usuario.registrar_usuario(
        registro=data['password'],
        fecha_de_operacion=datetime.datetime.now(),
        usuario_operacion=2
        )

        usuario_dict = {column.name: getattr(nuevo_usuario, column.name) for column in nuevo_usuario.__table__.columns if getattr(nuevo_usuario, column.name) is not None}
        
        return jsonify({'message': 'Usuario creado exitosamente'})
        # return jsonify(usuario_dict)
    
    except Exception as e:
        print(e)
        return jsonify({'message': 'Hubo un error al crear el usuario'})

@app.route('/usuarios/<int:id_usuario>', methods=['PUT'])
def actualizar_usuario(id_usuario):
    try:
        # Obtener el usuario por id y su último registro
        usuario = Usuario.query.get(id_usuario)
        
        # Obtener el registro por usuario_id que tenga fecha_operacion más reciente
        registro = UsuarioRegistro.query.filter_by(id_usuario=id_usuario).order_by(UsuarioRegistro.fecha_operacion.desc()).first()
                
        data = request.get_json()

        if usuario is None:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
         # Validar que el usuario por nro_doc y por login no exista
        usuario_nro_doc = Usuario.query.filter_by(nro_doc=data['nro_doc']).first()
        if usuario_nro_doc and usuario_nro_doc.id_usuario != id_usuario:
            return jsonify({'message': 'Ya existe un usuario con ese nro_doc'})
        
        usuario_login = Usuario.query.filter_by(login=data['login']).first()
        if usuario_login and usuario_login.id_usuario != id_usuario:
            return jsonify({'message': 'Ya existe un usuario con ese login'})
        
        # Validar el formato del email con expresiones regulares
        # Validar que el email no exista.
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data["mail"]):
            return jsonify({'message': 'El mail no tiene un formato válido'})
        
        # Validar que el password tenga al menos 8 caracteres
        if len(data['password']) < 8:
            return jsonify({'message': 'El password debe tener al menos 8 caracteres'})
        
        # Validar que el password tenga al menos una letra mayúscula, una minúscula y un número
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$', data["password"]):
            return jsonify({'message': 'El password debe tener al menos una letra mayúscula, una minúscula y un número'})
        
        # Editar los campos de usuario y de registro que se hayan modificado, los que no fueron modificados no se deben editar
        if data['nombre'] != usuario.nombre:
            usuario.nombre = data['nombre']
        if data['nro_doc'] != usuario.nro_doc:
            usuario.nro_doc = data['nro_doc']
        if data['login'] != usuario.login:
            usuario.login = data['login']
        if data['mail'] != usuario.mail:
            usuario.mail = data['mail']
        if md5(data['password']) != registro.registro:
            registro.registro = md5(data['password'])
            registro.fecha_de_operacion = datetime.datetime.now()
            registro.usuario_operacion = 2            
        
        # Actualizar el usuario
        usuario.fecha_modificacion = datetime.datetime.now()

        # Guardar los cambios
        db.session.commit()

        return jsonify({"message": "Usuario actualizado exitosamente"})

    except Exception as e:
        print(e)
        return jsonify({"error": "Hubo un error al actualizar el usuario"}), 500


@app.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
def eliminar_usuario(id_usuario):
    try:
        usuario = Usuario.query.get(id_usuario)
        if usuario is None:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Eliminar registros relacionados en UsuarioRegistro
        UsuarioRegistro.query.filter_by(id_usuario=id_usuario).delete()

        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"message": "Usuario eliminado exitosamente"})
    except Exception as e:
        print(e)
        return jsonify({"error": "Hubo un error al eliminar el usuario"}), 500

if __name__ == '__main__':
    app.run(debug=True)