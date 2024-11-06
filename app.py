from flask import Flask, redirect, render_template,request, url_for, flash, make_response, send_file
from io import BytesIO
from flask_mysqldb import MySQL
import pickle
import pandas as pd

# Connect to Database
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'welding'
mysql = MySQL(app)

# load model
with open('model.pkl', 'rb') as file:
    model = pickle.load(file)


@app.route('/', methods=['POST', 'GET'])
def login():
    # Mengambil cookie 'username'
    cookie = request.cookies.get('username')

    # Pengecekan apakah cookie ada dan valid
    if cookie:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_user WHERE username = %s", (cookie,))
        user_cookie = cursor.fetchone()
        cursor.close()

        if user_cookie:
            return redirect(url_for('solo'))

    # Jika cookie tidak ditemukan, periksa apakah method POST digunakan untuk login
    if request.method == "POST":
        # Ambil data dari form
        username = request.form['username']
        password = request.form['password']

        # Query ke database untuk cek username dan password
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_user WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        # Cek apakah user ditemukan
        if user:
            resp = make_response(redirect(url_for('solo')))  # Redirect ke halaman 'solo'
            resp.set_cookie('username', username)  # Set cookie 'username'
            return resp
        else:
            flash("Username atau password salah!", "error")
            return render_template('index.html')
    else:
        # Tampilkan halaman login jika request method bukan POST
        return render_template('index.html')
    
    

@app.route('/solo')
def solo():
    cookie = request.cookies.get('username')
    if cookie:
        cursor = mysql.connection.cursor()
        # Query ke database untuk mencari user berdasarkan cookie username
        cursor.execute("SELECT * FROM tb_user WHERE username = %s", (cookie,))
        user_cookie = cursor.fetchone()
        cursor.execute("SELECT * FROM tbl_schedule")
        schedules = cursor.fetchall()
        cursor.execute("SELECT * FROM tbl_component1")
        component1 = cursor.fetchall()
        cursor.execute("SELECT * FROM tbl_component2")
        component2 = cursor.fetchall()

        if user_cookie:
            return render_template('dashboard.html', schedules=schedules, component1 = component1, component2 = component2)
        else:
            return render_template('index.html')
   
        
    else:
        return render_template('index.html')


@app.route("/predict", methods=["GET", "POST"])
def predict():

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tbl_schedule")
    schedules = cursor.fetchall()
    cursor.execute("SELECT * FROM tbl_component1")
    component1 = cursor.fetchall()
    cursor.execute("SELECT * FROM tbl_component2")
    component2 = cursor.fetchall()

    # Ambil data dari form
    size = float(request.form.get('Size'))
    component_1 = request.form.get('Component1')
    component_2 = request.form.get('Component2')
    Schedule = request.form.get('Schedule')

    # input_data = [6.0, '40S', 'PIPE', 'FLANGE']

    input_data = {
    'Size': size,
    'Schedule': Schedule,
    'COMPONENT1': [component_1],
    'COMPONENT2': [component_2],
}

    # Konversi input_data menjadi array NumPy (jika model mengharapkannya)
    input_data = pd.DataFrame(input_data)

    X_train = pd.read_excel('kolom.xlsx')
    df_baru_encoded  = pd.get_dummies(input_data)
    df_baru_encoded = df_baru_encoded.reindex(columns=X_train.columns, fill_value=0)
    # Buat prediksi menggunakan model
    prediction = model.predict(df_baru_encoded)[0]

    cursor.execute(
        "INSERT INTO tb_welding (date, size, component1, component2, schedule, predict) VALUES (NOW(),%s, %s, %s, %s, %s);",
        (size, component_1, component_2, Schedule, prediction)
    )

    # Commit perubahan ke database
    mysql.connection.commit()
    cursor.close()
    
    # Buat response
    return render_template("dashboard.html",schedules=schedules, component1 = component1, component2 = component2, prediction="{}".format(prediction))

@app.route('/multi')
def multi():
    cookie = request.cookies.get('username')
    if cookie:
        # Query ke database untuk mencari user berdasarkan cookie username
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_user WHERE username = %s", (cookie,))
        user_cookie = cursor.fetchone()
        cursor.close()

        if user_cookie:
            return render_template('multi.html')
        else:
            return render_template('index.html')
     
    else:
        return render_template('index.html')

@app.route('/multipred', methods=['POST'])
def multipred():
    cookie = request.cookies.get("username")
    if cookie:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_user WHERE username = %s", (cookie,))
        user_cookie = cursor.fetchone()
        cursor.close()
        X_train = pd.read_excel('kolom.xlsx')

        if user_cookie:
            upload = request.files.get('upload')
            data = pd.read_excel(upload)
            encode = pd.get_dummies(data)
            reindex = encode.reindex(columns=X_train.columns, fill_value=0)
            prediction = model.predict(reindex)
            data['Location'] = prediction
            # menggubah dataframe ke excel
            data.to_excel('predict.xlsx', index=False)
            return send_file('predict.xlsx', as_attachment=True)
            
        else:
            return render_template('index.html')
     
    else:
        return render_template('index.html')


@app.route('/history')
def history():
    cookie = request.cookies.get('username')
    if cookie:
        # Query ke database untuk mencari user berdasarkan cookie username
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_user WHERE username = %s", (cookie,))
        user_cookie = cursor.fetchone()

        cursor.execute("SELECT * FROM tb_welding")
        welding = cursor.fetchall()
        cursor.close()

        if user_cookie:
            return render_template('history.html', welding = welding)
        else:
            return render_template('index.html')
   
        
    else:
        return render_template('index.html')

@app.route('/download')
def download():
    cookie = request.cookies.get('username')
    if cookie:
        # Query ke database untuk mencari user berdasarkan cookie username
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_user WHERE username = %s", (cookie,))
        user_cookie = cursor.fetchone()
        
        if user_cookie:
            cursor.execute("SELECT * FROM tb_welding")
            welding = cursor.fetchall()
            cursor.close()  # Tutup cursor setelah selesai digunakan

            # Konversi hasil query ke DataFrame
            welding_df = pd.DataFrame(welding, columns=['no', 'date', 'size', 'component1', 'component2', 'schedule', 'predict'])
            
            # Membuat file Excel dalam memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                welding_df.to_excel(writer, index=False, sheet_name='History Welding')

            # Menyiapkan respons untuk mengunduh file
            response = make_response(output.getvalue())
            response.headers["Content-Disposition"] = "attachment; filename=History_Welding.xlsx"
            response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            return response
        
        else:
            cursor.close()  # Tutup cursor sebelum mengembalikan halaman
            return render_template('index.html')
    else:
        return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

@app.route('/go-back')
def go_back():
    return redirect(request.referrer or url_for('index'))

@app.route('/logout')
def logout():
    resp = make_response(render_template('index.html'))
    resp.delete_cookie('username')
    return resp

if __name__ == "__main__":
    app.run(debug=True, port=5001)

