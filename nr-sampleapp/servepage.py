from flask import Flask, render_template
from random import randint
import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file
config.read('config.ini')

# Get the values
NR_ACCOUNT_ID = config.get('DEFAULT', 'NR_ACCOUNT_ID')
NR_LICENSE_KEY = config.get('DEFAULT', 'NR_LICENSE_KEY')
NR_AGENT_ID = config.get('DEFAULT', 'NR_AGENT_ID')

app = Flask(__name__)

@app.route('/')
def index():
    return  render_template('index.html',NR_ACCOUNT_ID=NR_ACCOUNT_ID, NR_LICENSE_KEY=NR_LICENSE_KEY, NR_AGENT_ID=NR_AGENT_ID, userId=randint(1, 1000))

if __name__ == '__main__':
    app.run(debug=True)
