from flask import Flask, render_template, jsonify
from trash import device

app = Flask(__name__)
app.debug = True

@app.route('/')
def map():
    return render_template('map.html')

@app.route('/trashcans')
def trashcans():
    return jsonify(device.trashcans())

if __name__ == '__main__':
    app.run()
