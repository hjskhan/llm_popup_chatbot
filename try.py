from flask import Flask, session, request, render_template

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    # Check if 'refreshed' key exists in session
    if 'refreshed' in session:
        refreshed = session['refreshed']
        # Clear the session variable after reading
        session.pop('refreshed', None)
    else:
        refreshed = False
    return render_template('try.html', refreshed=refreshed)

@app.route('/refresh', methods=['POST'])
def refresh():
    # Set 'refreshed' session variable to True
    session['refreshed'] = True
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)
