from flask import Flask, render_template, redirect, request, session

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"]


@app.route("/")
def hello():
    hi = "hello"
    return render_template('index.html', hi=hi)

if __name__ == "__main__":
    app.run()