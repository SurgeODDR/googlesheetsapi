from flask import Flask, jsonify
import logging
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import json  # add this line

# Set up Flask
app = Flask(__name__)

# Set up logging
handler = logging.FileHandler('app.log')  # log to a file
handler.setLevel(logging.INFO)  # log INFO level and above
app.logger.addHandler(handler)  # attach the handler to the app's logger

@app.route('/format_sheets', methods=['GET'])
def format_sheets():
    try:
        # Fetch the Google service account credentials from Azure Key Vault
        vault_url = "https://keyvaultxscrapingoddr.vault.azure.net/"
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=vault_url, credential=credential)
        secret_name = "YT-Scraper-web-googleservicekey"
        credentials_json_str = secret_client.get_secret(secret_name).value

        # Parse the JSON string into a Python dictionary
        credentials_dict = json.loads(credentials_json_str)

        # Set up Google Sheets API client
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(credentials)

        # Open the spreadsheet by title
        spreadsheet = client.open("twitch_data")

        # Format all sheets
        for worksheet in spreadsheet.worksheets():
            cell_list = worksheet.range('A1:Z1000')  # Adjust the range if you expect more data
            for cell in cell_list:
                cell.background = "#00FF00"  # lime green
            worksheet.update_cells(cell_list)

        return jsonify(success=True)

    except Exception as e:
        app.logger.exception(e)  # Log the exception
        return jsonify(error=str(e)), 500

# Define error handler for 500 status code
@app.errorhandler(500)
def server_error(e):
    app.logger.exception(e)  # Log the exception
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run()
