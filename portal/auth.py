from flask import Flask, render_template

    @app.route('/login', methods=('GET', 'POST'))
    def login():
            if request.method == 'POST':
                print('Lets get it started!')
                email = request.form['email']
                password = request.form['password']
                print(email)
                connection = psycopg2.connect(database = "portal")
                cursor = connection.cursor()
                user = cursor.execute('SELECT * FROM user WHERE email = %s', (email).fetchone()
                connection.commit()
                cursor.close()
                connection.close()
        return render_template('login.html')
