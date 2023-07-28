import logging
import sys
from flask import Flask, jsonify, current_app as app
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import json
from googleapiclient.discovery import build

# Configure root logging to print at the INFO level or higher to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

app = Flask(__name__)

@app.route('/format_sheets', methods=['GET'])
def format_sheets():
    try:
        logging.info("Fetching the Google service account credentials from Azure Key Vault...")
        vault_url = "https://keyvaultxscrapingoddr.vault.azure.net/"
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=vault_url, credential=credential)
        secret_name = "YT-Scraper-web-googleservicekey"
        credentials_json_str = secret_client.get_secret(secret_name).value

        logging.info(f"Fetched credentials: {credentials_json_str}")
        credentials_dict = json.loads(credentials_json_str)

        logging.info("Setting up Google Sheets API client...")
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(credentials)

        logging.info("Opening the spreadsheet...")
        spreadsheet = client.open("twitch_data")

        # Create a Sheets API service
        service = build('sheets', 'v4', credentials=credentials)

        logging.info("Formatting all sheets...")
        for worksheet in spreadsheet.worksheets():
            logging.info(f"Processing worksheet: {worksheet.title}")

            request = {
                "requests": [
                    {
                        "addConditionalFormatRule": {
                            "rule": {
                                "ranges": [{
                                    "sheetId": worksheet.id,
                                    "startRowIndex": 1,
                                    "endRowIndex": worksheet.row_count,
                                    "startColumnIndex": 1,
                                    "endColumnIndex": worksheet.col_count
                                }],
                                "booleanRule": {
                                    "format": {
                                        "backgroundColor": {
                                            "red": 0.4,
                                            "green": 0.8,
                                            "blue": 0.4
                                        }
                                    },
                                    "condition": {
                                        "type": "TEXT_CONTAINS",
                                        "values": [
                                            {
                                                "userEnteredValue": "1000"
                                            }
                                        ]
                                    }
                                }
                            },
                            "index": 0
                        }
                    }
                ]
            }
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet.id, body=request).execute()

            logging.info(f"Formatted worksheet: {worksheet.title}")

        return jsonify(success=True)

    except Exception as e:
        logging.exception(e)
        return jsonify(error=str(e)), 500

@app.errorhandler(500)
def server_error(e):
    logging.exception(e)
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run()
