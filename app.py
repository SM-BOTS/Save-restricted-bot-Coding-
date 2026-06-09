from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello from Koyeb'


if __name__ == "__main__":
    app.run()

# DONT REMOVE CREDITS
# Developer: [ Eva Rose ] (https://t.me/EvaRoseX)
# Join TG Channel: https://t.me/ERBotsUpdate
# Ask Doubt On Telegram: @EvaRoseX
# DEVELOPER: BY EVA ROSE
