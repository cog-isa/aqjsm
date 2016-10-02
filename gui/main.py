from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("test_template.html",
                           left_side='taken from main.py',
                           right1='right1',
                           right2='right2',
                           variable1="change!!!!")

if __name__ == "__main__":
    app.run()