from flask import Flask, jsonify, current_app as app
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import json

app = Flask(__name__)

@app.route('/format_sheets', methods=['GET'])
def format_sheets():
    try:
        app.logger.info("Fetching the Google service account credentials from Azure Key Vault...")
        vault_url = "https://keyvaultxscrapingoddr.vault.azure.net/"
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=vault_url, credential=credential)
        secret_name = "YT-Scraper-web-googleservicekey"
        credentials_json_str = secret_client.get_secret(secret_name).value

        app.logger.info(f"Fetched credentials: {credentials_json_str}")
        credentials_dict = json.loads(credentials_json_str)

        app.logger.info("Setting up Google Sheets API client...")
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(credentials)

        app.logger.info("Opening the spreadsheet...")
        spreadsheet = client.open("twitch_data")

        app.logger.info("Formatting all sheets...")
        for worksheet in spreadsheet.worksheets():
            app.logger.info(f"Processing worksheet: {worksheet.title}")
            cell_list = worksheet.range('A1:Z1000')
            for cell in cell_list:
                cell.background = "#00FF00"
            worksheet.update_cells(cell_list)
            app.logger.info(f"Updated {len(cell_list)} cells in worksheet: {worksheet.title}")

        return jsonify(success=True)

    except Exception as e:
        app.logger.exception(e)
        return jsonify(error=str(e)), 500

@app.errorhandler(500)
def server_error(e):
    app.logger.exception(e)
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run()
