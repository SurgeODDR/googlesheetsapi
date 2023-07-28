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

        logging.info("Formatting all sheets...")
        for worksheet in spreadsheet.worksheets():
            logging.info(f"Processing worksheet: {worksheet.title}")
            cell_list = worksheet.range('A1:Z1000')
            for cell in cell_list:
                cell.background = "#FF0000"  # Red background color
                cell.textFormat = {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1},  # White font color
                                   'fontSize': 12,  # Font size
                                   'bold': True,  # Bold text
                                   'italic': False}  # Non-italic text
                cell.horizontalAlignment = "CENTER"  # Center-aligned text
            worksheet.update_cells(cell_list, "USER_ENTERED")
            logging.info(f"Updated {len(cell_list)} cells in worksheet: {worksheet.title}")

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
