# psycopg2 es un adaptador de postgresql para python que nos permite conectarnos a la base de datos
# g es una variable global que se utiliza para almacenar datos 
# que pueden ser accesibles desde cualquier parte de la aplicación durante el ciclo de vida de una solicitud.
# El objeto g se inicializa automáticamente para cada solicitud y se destruye al finalizar la solicitud.	

from flask import Flask, g, jsonify, request
import psycopg2

app = Flask(__name__)
app.config["DEBUG"] = True
# Configuración de la conexión a la base de datos
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = psycopg2.connect(
                                user="postgres",
                                password="PIKqPhxx35Ymhm3MIgdR",
                                host="containers-us-west-17.railway.app",
                                port="5679",
                                database="railway"
                                )
    return db

# El decorador @app.teardown_appcontext se utiliza para registrar una función 
# que se ejecutará al final de cada solicitud y que se encargará de cerrar la conexión de base de datos si es necesario.
# getattr() es una función integrada de Python que devuelve el valor del atributo de un objeto.
# _database es el nombre del atributo que se utiliza para almacenar la conexión a la base de datos en el objeto g.
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
    
@app.route('/', methods=['GET'])
def home():

    # Conexión a la base de datos
    conn = get_db()

    # crear un cursor para ejecutar sentencias SQL
    cursor = conn.cursor()

    # ejecutar sentencia SQL para obtener el número de libros
    # execute() es un método de la clase cursor que ejecuta una sentencia SQL en la base de datos
    cursor.execute("SELECT * FROM books_table")

    # fetchall() es un método de la clase cursor que se utiliza para recuperar todas las filas restantes
    # de un conjunto de resultados de una consulta SQL ejecutada mediante el cursor.
    totalRows = cursor.fetchall()
    numero_libros = len(totalRows)

    # cerrar el cursor y la conexión
    cursor.close()

    home_display = f"""
    <h1>BOOKS API</h1><p>This site is a prototype API.
    This is a collection of novels.
    We currently store {numero_libros} books</p>"""

    return home_display

# 1.Ruta para obtener todos los libros
@app.route('/resources/books/all', methods=['GET'])
def get_all():

    # Conexión a la base de datos
    conn = get_db()

    # crear un cursor para ejecutar sentencias SQL
    cursor = conn.cursor()

    # Cuando se llama al método execute(), el cursor envía la consulta SQL a la base de datos para su ejecución.
    cursor.execute("SELECT * FROM books_table")
    all_books = cursor.fetchall()

    # cerrar el cursor
    cursor.close()
    
    return jsonify(all_books)

# 2.Ruta para añadir un libro
@app.route('/resources/book/add', methods=['POST'])
def agregar_libro():
    # Obtener los datos del libro del cuerpo de la solicitud
    datos = request.get_json()

    author = datos['author']
    year = datos['year']
    title = datos['title']
    description = datos['description']

    # Conexión a la base de datos
    conn = get_db()

    # crear un cursor para ejecutar sentencias SQL
    cursor = conn.cursor()

    # Comprobar si el libro ya existe en la base de datos
    cursor.execute("SELECT * FROM books_table WHERE title = %s", (datos['title'],))
    libro = cursor.fetchone()

    if libro is not None:
        return jsonify({'mensaje': 'El libro ya existe en la base de datos'})

    else:
        # Obtener el último id de la tabla libros
        cursor.execute("SELECT id FROM books_table ORDER BY id DESC LIMIT 1")
        resultado = cursor.fetchone()
        id_book = resultado[0] + 1
        
        # Insertar el libro en la base de datos
        cursor.execute("INSERT INTO books_table (id, author, year, title, description) VALUES (%s, %s, %s, %s, %s)", (id_book, author, year, title, description))
        conn.commit()
        
        # cerrar el cursor
        cursor.close()

        # Devolver una respuesta satisfactoria
        return jsonify({'mensaje': 'El libro se ha agregado correctamente'})

# 3.Ruta para añadir un libro con parámetros
@app.route('/resources/book/add_parameters', methods=['POST'])
def post_book_parameters():
    data = {}
    if 'id' in request.args:
        data['id_book'] = request.args['id']
    if 'title' in request.args:
        data['title'] = request.args['title']
    if 'author' in request.args:
        data['author'] = request.args['author']
    if 'description' in request.args:
        data['description'] = request.args['description']
    if 'year' in request.args:
        data['year'] = request.args['year']

    # Conexión a la base de datos
    conn = get_db()

    # crear un cursor para ejecutar sentencias SQL
    cursor = conn.cursor()

    # Comprobar si el libro ya existe en la base de datos
    cursor.execute("SELECT * FROM books_table WHERE title = %s", (data['title'],))
    libro = cursor.fetchone()

    if libro is not None:
        return jsonify({'mensaje': 'El libro ya existe en la base de datos'})

    else:
        # Insertar el libro en la base de datos
        cursor.execute("INSERT INTO books_table (id, author, year, title, description) VALUES (%s, %s, %s, %s, %s)", (data['id_book'], data['author'], data['year'], data['title'], data['description']))
        conn.commit()
        
        # cerrar el cursor
        cursor.close()

        # Devolver una respuesta satisfactoria
        return jsonify({'mensaje': 'El libro se ha agregado correctamente'})
    
# 4.Ruta para eliminar un libro por su ID
@app.route('/resources/book/delete/<int:id>', methods=['DELETE'])
def delete_book(id):

    # Conexión a la base de datos
    conn = get_db()

    # crear un cursor para ejecutar sentencias SQL
    cursor = conn.cursor()

    # Ejecutar la consulta SQL para comprobar si el libro existe
    cursor.execute("SELECT * FROM books_table WHERE id = %s", (id,))
    libro = cursor.fetchone()
    
    # Si el libro no existe, devolver una respuesta JSON indicándolo
    if libro is None:
        return jsonify({'mensaje': 'El libro no existe en la base de datos'})
    
    else:
        # Ejecutar la consulta SQL para eliminar el libro con el ID especificado
        cursor.execute("DELETE FROM books_table WHERE id = %s", (id,))

        # Confirmar la transacción
        conn.commit()

        # cerrar el cursor
        cursor.close()

        # Retornar una respuesta JSON indicando que el libro ha sido eliminado
        return jsonify({'El libro ha sido eliminado de la base de datos'})

# 5.Ruta para modificar un libro
@app.route('/resources/book/update', methods=['PUT'])
def update_book():
    year = request.args['year']
    title = request.args['title']

    # Conexión a la base de datos
    conn = get_db()

    # crear un cursor para ejecutar sentencias SQL
    cursor = conn.cursor()
    
    # Comprobar si el libro ya existe en la base de datos
    cursor.execute("SELECT * FROM books_table WHERE title = %s", (title,))
    libro = cursor.fetchone()

    if libro is None:
        return jsonify({'mensaje': 'El libro no existe en la base de datos'})
    
    else:
        # Actualizar el año de publicación del libro
        cursor.execute("UPDATE books_table SET year = %s WHERE title = %s", (year, title))
        conn.commit()

    return jsonify({'mensaje': 'El libro se ha actualizado correctamente'})

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run()