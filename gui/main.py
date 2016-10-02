from flask import Flask, render_template, send_from_directory
from gui.graph_gen import s

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("test_template.html",
                           left_side='taken from main.py',
                           right1='right1',
                           right2='right2',
                           graph=s,
                           variable1="change!!!!")

# @app.route('/<templates:sigma.js>')
# def send_js(path):
#     return send_from_directory('templates', sigma.js)


if __name__ == "__main__":
    app.run(debug=True)