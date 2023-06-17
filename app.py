from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2 #pip install psycopg2 
import psycopg2.extras
from src import master_password
from Crypto.Protocol.KDF import scrypt
from src import normal_password

 
app = Flask(__name__)
app.secret_key = "diego-ale-seguridad"
 
DB_HOST = "localhost"
DB_NAME = "seguridad-proyecto"
DB_USER = "postgres"
DB_PASS = "Manzana12345678"
 
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
 
# Decorator function to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = conn.cursor()
        # Check if the entered credentials are valid
        cur.execute('SELECT * FROM users WHERE username = %s', [username])
        user = cur.fetchone()

        if user and master_password.check_password(password, bytes(user[2])):
            # Set a session variable to indicate that the user is logged in
            session['logged_in'] = True
            session['username'] = user[1]  # username is stored at index 1 in the users table
            session['user_id'] = user[0]
            salt = bytes(user[2])[:29]

            app.secret_key = scrypt(password, salt, 16, N=2**14, r=8, p=1)

            flash('Login successful!')
            return redirect(url_for('Index'))
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('login.html')

@app.route('/create-user', methods=['POST'])
def create_user():
    new_username = request.form['new_username']
    new_password = request.form['new_password']
    new_password = master_password.hash_password(new_password)
    cur = conn.cursor()
    
    cur.execute("INSERT INTO users (username, master_password) VALUES (%s, %s)", (new_username, new_password))
    conn.commit()
    flash('New user created successfully!')
    return redirect(url_for('login'))

@app.route('/index')
@login_required 
def Index():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("SELECT * FROM passwords WHERE user_id = %s", [session.get("user_id")]) # Execute the SQL
    list_passwords = cur.fetchall()
    return render_template('index.html', list_passwords = list_passwords)
 

@app.route('/add_password', methods=['POST'])
@login_required 
def add_password():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        page_name = request.form['page_name']
        destination_url = request.form['destination_url']
        encrypted_password = request.form['encrypted_password']

        nonce, encrypted_password, tag = normal_password.AES_Encrypt(encrypted_password, app.secret_key)
        
        cur.execute("INSERT INTO passwords (user_id, page_name, destination_url, encrypted_password, authentication_tag, nonce) VALUES (%s,%s,%s,%s,%s,%s)", 
                    (session.get("user_id"), page_name, destination_url, 
                     psycopg2.Binary(encrypted_password),
                     psycopg2.Binary(tag), 
                     psycopg2.Binary(nonce)))
        conn.commit()
        flash('New password Added successfully')
        return redirect(url_for('Index'))
    
 

@app.route('/edit/<page_name>', methods = ['POST', 'GET'])
@login_required 
def get_password(page_name):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM passwords WHERE page_name = %s and user_id = %s', (page_name, session.get("user_id")))
    data = cur.fetchall()
    cur.close()
    data[0][3] = normal_password.AES_Decrypt(
        bytes(data[0][3]),
        app.secret_key,
        bytes(data[0][5]),
        bytes(data[0][4])
    )    
    return render_template('edit.html', password = data[0])
 


@app.route('/update/<page_name>', methods=['POST'])
@login_required 
def update_password(page_name):
    if request.method == 'POST':
        new_page_name = request.form['page_name']
        destination_url = request.form['destination_url']
        encrypted_password = request.form['encrypted_password']
        
        nonce, encrypted_password, tag = normal_password.AES_Encrypt(encrypted_password, app.secret_key)
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE passwords
            SET page_name = %s,
                destination_url = %s,
                encrypted_password = %s,
                authentication_tag = %s,
                nonce = %s
            WHERE page_name = %s and user_id = %s
        """, (new_page_name, 
              destination_url, 
              encrypted_password,  tag, nonce, page_name, session.get("user_id")))
        flash('Password Updated Successfully')
        conn.commit()
        return redirect(url_for('Index'))
    

 
@app.route('/delete/<string:page_name>', methods = ['POST','GET'])
@login_required 
def delete_password(page_name):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM passwords WHERE page_name = %s and user_id = %s', (page_name, session.get("user_id")))
    conn.commit()
    flash('Page Removed Successfully')
    return redirect(url_for('Index'))
 
if __name__ == "__main__":
    app.run(debug=True)
