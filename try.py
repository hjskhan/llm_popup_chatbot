from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        session['url'] = url
    else:
        session.pop('url', None)

    return render_template('try.html', url=session.get('url'))

if __name__ == '__main__':
    app.run(debug=True)
