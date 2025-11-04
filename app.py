from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def get_data():
    # Read data from the backend file
    with open('data.json', 'r') as file:
        data = json.load(file)
    return jsonify(data)  # Return JSON response

if __name__ == '__main__':
    app.run(debug=True)
