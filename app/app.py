from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route('/random-data', methods=['GET'])
def get_random_data():
    # Generate random data (replace with your actual data generation logic)
    random_value = random.randint(1, 100)
    return jsonify({"random_metric": random_value})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

