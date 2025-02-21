import gspread
from oauth2client.service_account import ServiceAccountCredentials

def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('google_sheets.json', scope)
    client = gspread.authorize(creds)
    return client

def open_sheet(sheet_name):
    client = authenticate_google_sheets()
    sheet = client.open(sheet_name).sheet1  # Open the first sheet of the specified Google Sheet
    return sheet

def add_data_to_google_sheets(name, subject, marks, attendance, study_hours, roll_number):
    sheet = open_sheet("GrowthMindsetData")  # Replace with your actual sheet name

    # Check if the roll number already exists in the sheet
    existing_data = sheet.get_all_records()
    if any(str(row['Roll Number']) == str(roll_number) for row in existing_data):
        print(f"Student with Roll Number {roll_number} already exists!")
    else:
        sheet.append_row([roll_number, name, subject, marks, attendance, study_hours])
        print(f"Data for student {name} added to Google Sheets!")
