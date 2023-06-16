#app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2 #pip install psycopg2 
import psycopg2.extras
 
app = Flask(__name__)
app.secret_key = "diego-ale-seguridad"
 
DB_HOST = "localhost"
DB_NAME = "seguridad-proyecto"
DB_USER = "postgres"
DB_PASS = "Manzana12345678"
 
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
 
@app.route('/')
def Index():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = "SELECT * FROM passwords"
    cur.execute(s) # Execute the SQL
    list_passwords = cur.fetchall()
    return render_template('index.html', list_passwords = list_passwords)
 
@app.route('/add_password', methods=['POST'])
def add_password():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        page_name = request.form['page_name']
        destination_url = request.form['destination_url']
        encrypted_password = request.form['encrypted_password']
        cur.execute("INSERT INTO passwords (page_name, destination_url, encrypted_password) VALUES (%s,%s,%s)", (page_name, destination_url, encrypted_password))
        conn.commit()
        flash('New password Added successfully')
        return redirect(url_for('Index'))
    
 
@app.route('/edit/<page_name>', methods = ['POST', 'GET'])
def get_password(page_name):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM passwords WHERE page_name = %s', (page_name,))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit.html', password = data[0])
 
@app.route('/update/<page_name>', methods=['POST'])
def update_student(page_name):
    if request.method == 'POST':
        new_page_name = request.form['page_name']
        destination_url = request.form['destination_url']
        encrypted_password = request.form['encrypted_password']
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE passwords
            SET page_name = %s,
                destination_url = %s,
                encrypted_password = %s
            WHERE page_name = %s
        """, (new_page_name, destination_url, encrypted_password, page_name))
        flash('Password Updated Successfully')
        conn.commit()
        return redirect(url_for('Index'))
 
@app.route('/delete/<string:page_name>', methods = ['POST','GET'])
def delete_password(page_name):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM passwords WHERE page_name = %s', (page_name,))
    conn.commit()
    flash('Page Removed Successfully')
    return redirect(url_for('Index'))
 
if __name__ == "__main__":
    app.run(debug=True)