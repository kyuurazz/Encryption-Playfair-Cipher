from flask import Flask, render_template, request, redirect, url_for, session
from playfair_encrypt import initializeMatrix, prepareText, playfairEncrypt
import sqlite3

app = Flask(__name__)

app.secret_key = 'secret_key_session'

# Inisialisasi Database SQLite
conn = sqlite3.connect('customer_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, nama TEXT, alamat TEXT, password TEXT, key TEXT)''')
conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('index.html')


# Fungsi Untuk Menyimpan Data Nasabah
@app.route('/simpan_data', methods=['POST'])
def simpan_data():
    nama = request.form['nama']
    alamat = request.form['alamat']
    password = request.form['password']
    key = request.form['key']

    # Inisialisasi matriks Playfair Cipher
    matrix = initializeMatrix(key)

    # Enkripsi password
    prepared_password = prepareText(password)
    encrypted_password = playfairEncrypt(prepared_password, matrix)

    # Simpan data nasabah ke database
    conn = sqlite3.connect('customer_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO customers (nama, alamat, password, key) VALUES (?, ?, ?, ?)", (nama, alamat, encrypted_password, key))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


# Fungsi Hapus Data Nasabah
@app.route('/hapus_data', methods=['POST'])
def hapus_data():
    customer_id = request.form.get('customer_id')
    
    # Hapus data nasabah berdasarkan customer_id
    conn = sqlite3.connect('customer_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('data'))


# Fungsi untuk mengambil informasi pengguna dari database
def get_user_info(nama, password):
    conn = sqlite3.connect('customer_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM customers WHERE nama = ? AND password = ?", (nama, password))
    user = c.fetchone()
    conn.close()

    if user:
        user_info = {
            'id': user[0],
            'nama': user[1],
            'alamat': user[2],
        }
        return user_info
    else:
        return None


# Fungsi Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nama = request.form['nama']
        password = request.form['password']

        # Mengambil informasi pengguna dari database
        user = get_user_info(nama, password)

        if user:
            # Jika pengguna valid, arahkan ke halaman profile dengan informasi pengguna
            return render_template('profile.html', user=user)
        else:
            # Jika pengguna tidak valid, arahkan kembali ke halaman login
            return render_template('login.html')

    return render_template('login.html')


# Fungsi Logout
@app.route('/logout')
def logout():
    # Hapus informasi sesi pengguna
    session.pop('user_id', None)

    # Redirect pengguna ke halaman login
    return redirect(url_for('login'))


# Fungsi Menampilkan Data Nasabah
@app.route('/data')
def data():
    conn = sqlite3.connect('customer_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM customers")
    data = c.fetchall()
    conn.close()
    return render_template('data.html', data=data)


# Fungsi Menampilkan Profile
@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        user = get_user_info(user_id)

        if user:
            return render_template('profile.html', user=user)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
