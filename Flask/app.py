from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

user = "jerry"
app = Flask(__name__)

# conexiones con base de datos MySQL
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1346"
app.config["MYSQL_DB"] = "HoraLibre"
#app.config["MYSQL_CURSORCLASS"] = 'DictCursor'
mysql = MySQL(app)

# settings
app.secret_key = "mysecretkey"

position = 0
layer = []
# 0-15
columns = ["Id", "Nivel", "Grado", "Campos", "Componentes", "Organizador1", "Organizador2",
           "ApEs", "ApEs_Detalle", "Escala_Sugerida", "Indicador1", "Indicador2", "Indicador3",
           "Indicador4", "Observaciones", "Activo"]

actual = ["Nivel", "Grado", "Campos", "Componentes", "ApEs"]

indicadores = ["Indicador1", "Indicador2", "Indicador3",
               "Indicador4"]

contenido_aprendizajes_esperados = (["ApEs_Detalle"], ["Escala_Sugerida"], ["Indicador1"], ["Indicador2"], ["Indicador3"],
                                    ["Indicador4"], ["Observaciones"], ["Activo"])

search_query = ["SELECT DISTINCT Nivel FROM main",
                "SELECT DISTINCT Grado FROM main WHERE Nivel = '{0}'",
                "SELECT DISTINCT Campos FROM main WHERE Nivel ='{0}' AND Grado ='{1}'",
                "SELECT DISTINCT Componentes FROM main WHERE Nivel ='{0}' AND Grado ='{1}' AND Campos ='{2}'"]

erase_query = ["DELETE FROM main WHERE Nivel = '{0}'",
               "DELETE FROM main WHERE Nivel='{0}' AND Grado ='{1}'",
               "DELETE FROM main WHERE Nivel='{0}'AND Grado='{1} AND Campos='{2}'"]

insert_query = ["INSERT INTO main(Nivel)VALUES('{0}')",
                "INSERT INTO main(Nivel,Grado) VALUES('{0}','{1}')",
                "INSERT INTO main(Campos) VALUES('{0}')WHERE Nivel='{1}' AND Grado ='{2}'"]

edit_query = ["SELECT DISTINCT Nivel FROM main WHERE Nivel = '{0}'",
              "SELECT DISTINCT Grado FROM main WHERE Nivel = '{0}' AND Grado ='{1}'",
              "SELECT DISTINCT Campos FROM main WHERE Nivel = '{0}' AND Grado = '{1} AND Campos ='{2}'"]

update_query = ["UPDATE main SET Nivel = '{0}' WHERE Nivel = '{1}'",
                "UPDATE main SET Grado = '{0}' WHERE Nivel = '{1}' AND Grado = '{2}'",
                "UPDATE main SET Campos = '{0}' WHERE Nivel = '{1}' AND Grado = '{2}'AND Campos ='{3}'"]
# parte de inicio de la applicacion

"""
Pagina de inicio de nuestra aplicacion dependiendo del nivel de nuestro navegador
 va a desplegar diferente informacion en la pantalla
"""

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

def es_admin():
    #Create Cursor
    cur = mysql.connection.cursor()
    #Make Query
    cur.execute("SELECT admin FROM users WHERE username = '{0}'".format(session['username']))
    #
    data = cur.fetchone()
    print("Data: ")
    print(data)
    print(type(data))
    if data[0] == 1:
        return True
    else:
        return False

def is_admin_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if es_admin():
            return f(*args,**kwargs)
        else:
            flash("Unauthorized, non-admin user","danger")
            return redirect(url_for('Index'))
    return wrap

#Navbar Home
@app.route ("/nav_home")
@is_logged_in
def nav_home():
    global position
    print("position: "+str(position))
    position = 0
    print("position: "+str(position))
    return redirect(url_for("Index"))
# Home
@app.route("/dashboard")
@is_logged_in
def Index():
    global actual
    global position
    global search_query
    cur = mysql.connection.cursor()
    try:
        print("Layer: ")
        print(layer)
        print("\n\n\n")
        if position == 0:
            cur.execute(search_query[0].format(""))
        elif position == 1:
            cur.execute(search_query[1].format(layer[0]))
        elif position == 2:
            cur.execute(search_query[2].format(layer[0], layer[1]))
        elif position >= 3:
            cur.execute(search_query[3].format(layer[0], layer[1], layer[2]))
        data = cur.fetchall()
        cur.close()
        print(type(data))
    except:
        flash("error")
    finally:
        print(data)
        print("position = "+str(position))

        return render_template("index.html", contactos=data, titulo=actual[position],admin=es_admin())


# User Control
@app.route("/control")
@is_logged_in
@is_admin_in
def control():
    form = RegisterForm(request.form)
    # Create cursor
    cur = mysql.connection.cursor()
    print("cur: "+str(type(cur)))
    # Get users
    cur.execute("SELECT * FROM users")

    all_users = cur.fetchall()
    print(all_users)
    # Close Cursor
    cur.close()
    return render_template("user_control.html", usuarios=all_users, form=form, admin=es_admin())


# accion de navegacion
@app.route("/next/<info>")
@is_logged_in
def next_block(info):  # info: String
    global layer
    global position
    try:
        if position <= 3:
            if position == 0:
                layer.append(info)
            else:
                layer.append(info)
            position = position + 1
    except:
        flash("error")
    finally:
        print("position: "+str(position))
        print("Layer: ")
        print(layer)
        return redirect(url_for("Index"))

# Back Button
@app.route("/back")
@is_logged_in
def back_block():
    global position
    global layer
    if position > 0:
        position = position - 1
        layer.pop()
        print(layer)
    return redirect(url_for("Index"))


    ########################################################
# ADD ApEs to DB
@app.route("/contactos", methods=["POST"])
@is_logged_in
def add_contact():
    global position
    if request.method == "POST":
        ids = request.form["id"]
        cur = mysql.connection.cursor()
        print("ids: ")
        print(ids)
        print("layer: ")
        print(layer)
        #try:
        if position == 0:
            cur.execute(insert_query[position].format(ids))
        elif position == 1:
            cur.execute(insert_query[position].format(layer[0],ids))
        else:
            pass
        mysql.connection.commit()
        flash("Base de Datos Actualizada Satisfactoriamente")
        #except:
            #flash("error")
        #finally:
        cur.close()
        return redirect(url_for("Index"))
######################################################################

# DELETE ApEs DB
@app.route("/delete/<string:id>")
@is_logged_in
def delete(id):
    global erase_query
    global position
    print("Username: "+str(session['username']))
    print(type(session['username']))
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO cambios(previous,new,username,columna)VALUES('{0}','{1}','{2}','{3}')".format(id,"Eliminado",session['username'],actual[position]))
    mysql.connection.commit()
    cur.execute(erase_query[position].format(id))
    mysql.connection.commit()
    flash("Contacto removido")
    return redirect(url_for("Index"))

# DELETE USERS
@app.route("/delete_usr/<string:id>")
@is_logged_in
@is_admin_in
def delete_usr(id):
    # Create Cursor
    cur = mysql.connection.cursor()

    # Get User to delete
    cur.execute("DELETE FROM users WHERE id='{0}'".format(id))

    # Commit Change
    mysql.connection.commit()
    flash("Contacto removido")

    # Close Connection
    cur.close()
    return redirect(url_for("control"))


# Edit DB
@app.route("/edit/<id>")
@is_logged_in
def edit(id):
    global position
    print("id: "+str(id))
    print("entered")
    #CREATE CURSOR
    cur = mysql.connection.cursor()
    #EXECUTE QUERY
    cur.execute(edit_query[position].format(id))#
    #FETCH DATA
    data = cur.fetchall()
    #CLOSE CURSOR DONT CLOSE FOR EDIT
    #cur.close()
    return render_template("edit-contact.html", contact=data[0], titulo=id, placeholder=actual[position])


# Update DB
@app.route("/update/<id>", methods=["POST"])
@is_logged_in
def update_contact(id):
    global position
    if request.method == "POST":
        ids = request.form["fullname"]
        cur = mysql.connection.cursor()
        if position == 0:
            cur.execute("INSERT INTO cambios(previous,new,username,columna)VALUES('{0}','{1}','{2}','{3}')".format(id,ids,session['username'],actual[position]))
            mysql.connection.commit()
            cur.execute(update_query[position].format(ids, id))
        mysql.connection.commit()
        flash("los datos han sido actualizados")
        cur.close()
        return redirect(url_for("Index"))

# Login
@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']
        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute(
            "SELECT password FROM users WHERE username = '{0}'".format(username))
        print("Result:")
        print(result)
        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            print(data)
            password = data[0]

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username
                

                flash('You are logged in', 'success')
                return redirect(url_for('Index'))
            else:
                error = 'Password not found'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# Registration Form
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

#User Registration
@app.route('/register', methods=['GET', 'POST'])
@is_logged_in
@is_admin_in
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        # Create Cursor
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = sha256_crypt.hash(str(request.form['password']))
        admin = request.form.getlist('admin')
        if not admin:
            is_admin = 0
        else:
            is_admin = 1
        print(is_admin)

        # Crate Cursor
        cur = mysql.connection.cursor()

        # Check for repeated usernames
        result = cur.execute(
            "SELECT * FROM users WHERE username = '{0}'".format(username))
        if result > 0:
            # Close Connection
            cur.close()

            flash("Username already taken", "danger")
        else:
            # Query
            cur.execute(
                "INSERT INTO users(name,email,username,password,admin)VALUES('{0}','{1}','{2}','{3}','{4}')".format(name, email, username, password, is_admin))
            # Commit to DB
            mysql.connection.commit()

            # Close Connection
            cur.close()

            flash("You are now registered and can login", "success")
            redirect(url_for("Index"))
            
    return render_template('register.html', form=form,admin=es_admin())




# Run Script
if __name__ == "__main__":
    app.run(port=3000, debug=True)
