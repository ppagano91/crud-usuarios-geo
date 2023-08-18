import hashlib

def md5(texto):
    # Crear un objeto hashlib.md5
    md5_hash = hashlib.md5()

    # Actualizar el objeto con los datos a los que se les calculará el hash
    md5_hash.update(texto.encode('utf-8'))

    # Obtener el hash MD5 en formato hexadecimal
    hash_md5 = md5_hash.hexdigest()

    return hash_md5