import threading
import time
import requests
from flask import Flask

app = Flask(__name__)

def send_get_request_periodically():
    while True:
        try:
            response = requests.get('https://gptanalyser2.azurewebsites.net/process')
            app.logger.info(f"Sent GET request. Response status: {response.status_code}")
        except Exception as e:
            app.logger.error(f"Failed to send GET request. Error: {e}")
        time.sleep(60)

@app.route('/')
def index():
    app.logger.info("Accessed root endpoint.")
    return "Server is running."

if __name__ == '__main__':
    # Configuring logging for Flask
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Start the background thread for sending GET requests
    threading.Thread(target=send_get_request_periodically, daemon=True).start()
    
    # Run the Flask server
    app.run(threaded=False, use_reloader=False)
