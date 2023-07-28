from flask import Flask
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = Flask(__name__)

@app.route('/')
def format_sheets():
    # Fetch credentials from Azure Key Vault
    key_vault_name = 'Keyvaultxscrapingoddr'
    KVUri = f"https://{key_vault_name}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)
    secret_value = client.get_secret("YT-Scraper-web-googleservicekey")

    # Use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_value.value, scope)
    client = gspread.authorize(creds)

    # Open the Google Spreadsheet using its name
    spreadsheet = client.open('twitch_data')  # Update with your Spreadsheet Name

    # Fetch all worksheets
    worksheets = spreadsheet.worksheets()

    # Loop through each worksheet
    for worksheet in worksheets:
        # Set the font size and make the header row bold
        cell_format = gspread.format.CellFormat(fontSize=10, textFormat=gspread.format.TextFormat(bold=True))
        worksheet.format("1:1", cell_format)

        # Freeze the header row
        worksheet.frozen_rows = 1

        # Additional formatting for 'geography' and 'demographics' sheets
        if worksheet.title == 'geography' or worksheet.title == 'demographics':
            # Assuming the username is in the first column
            usernames = worksheet.col_values(1)
            data = worksheet.get_all_values()

            # Move the username column to the last position
            for i, row in enumerate(data):
                row.append(row.pop(0))
                worksheet.insert_row(row, i+1)

            # Delete the original username column
            worksheet.delete_columns(1)

    return "Formatted the sheets successfully", 200

if __name__ == '__main__':
    app.run(debug=True)
