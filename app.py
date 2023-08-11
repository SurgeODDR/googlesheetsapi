import logging
import sys
import threading
import time
import requests
from flask import Flask, jsonify
# ... [Your other imports]

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

app = Flask(__name__)

# Function to send a GET request every minute
def send_get_request_periodically():
    while True:
        try:
            response = requests.get('https://gptanalyser2.azurewebsites.net/process')
            logging.info(f"Sent GET request. Response status: {response.status_code}")
        except Exception as e:
            logging.exception("Failed to send GET request")
        time.sleep(60)

# Run the function in a background thread
threading.Thread(target=send_get_request_periodically, daemon=True).start()

# ... [Your existing Flask routes and functions]

if __name__ == '__main__':
    app.run()
