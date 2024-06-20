import time
import requests
from flask import Flask, request, jsonify
from collections import deque

app = Flask(__name__)

WINDOW_SIZE = 10
TIMEOUT = 0.5

# In-memory storage for numbers
numbers_store = {
    'p': deque(maxlen=WINDOW_SIZE),
    'f': deque(maxlen=WINDOW_SIZE),
    'e': deque(maxlen=WINDOW_SIZE),
    'r': deque(maxlen=WINDOW_SIZE)
}

# Dummy third-party API URL (replace with the actual URL)
API_URL_TEMPLATE = "https://thirdpartyserver.com/api/numbers/{id}"

def fetch_number(id_type):
    try:
        response = requests.get(API_URL_TEMPLATE.format(id=id_type), timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json().get('number')
    except requests.RequestException:
        pass
    return None

def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

@app.route('/numbers/<id_type>', methods=['GET'])
def get_numbers(id_type):
    if id_type not in numbers_store:
        return jsonify({'error': 'Invalid ID type'}), 400

    before_numbers = list(numbers_store[id_type])
    new_number = fetch_number(id_type)
    
    if new_number is not None and new_number not in numbers_store[id_type]:
        if len(numbers_store[id_type]) >= WINDOW_SIZE:
            numbers_store[id_type].popleft()
        numbers_store[id_type].append(new_number)

    after_numbers = list(numbers_store[id_type])
    average = calculate_average(after_numbers)
    
    response = {
        'before': before_numbers,
        'after': after_numbers,
        'average': average
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
