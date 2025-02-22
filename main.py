import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import random

st.markdown("""
    <style>
        body {
            background-color: #f4f7fc;
            font-family: 'Arial', sans-serif;
            color: #4A4A4A;
        }
        .sidebar .sidebar-content {
            background-color: #3B7D8B;
            color: white;
        }
        .stButton>button {
            background-color: #3B7D8B;
            color: white;
            border-radius: 5px;
            padding: 12px;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #2F5C66;
        }
        h1, h2, h3 {
            color: #2A4D5B;
        }
        .stDataFrame {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            padding: 15px;
            margin-top: 20px;
        }
        .stFileUploader>div {
            background-color: #3B7D8B;
            color: white;
            border-radius: 5px;
            padding: 10px;
            text-align: center;
        }
        .stSelectbox, .stTextInput, .stNumberInput {
            background-color: #E2F2F5;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .stTextInput input, .stNumberInput input {
            padding: 10px;
        }
        .stTextInput label, .stNumberInput label {
            font-weight: bold;
        }

        /* Responsive design */
        @media (max-width: 768px) {
            body {
                font-size: 14px;
            }
            h1, h2, h3 {
                font-size: 18px;
            }
            .stButton>button {
                font-size: 14px;
                padding: 10px;
            }
            .stDataFrame {
                padding: 10px;
            }
            .stFileUploader>div {
                padding: 8px;
            }
            .stSelectbox, .stTextInput, .stNumberInput {
                font-size: 14px;
                padding: 8px;
            }
        }

        @media (max-width: 480px) {
            body {
                font-size: 12px;
            }
            h1, h2, h3 {
                font-size: 16px;
            }
            .stButton>button {
                font-size: 12px;
                padding: 8px;
            }
            .stDataFrame {
                padding: 8px;
            }
            .stFileUploader>div {
                padding: 6px;
            }
            .stSelectbox, .stTextInput, .stNumberInput {
                font-size: 12px;
                padding: 6px;
            }
        }
    </style>
""", unsafe_allow_html=True)

def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_sheets_credentials"], scope)
    client = gspread.authorize(creds)
    return client

def open_sheet(sheet_name):
    client = authenticate_google_sheets()
    sheet = client.open(sheet_name).sheet1  
    return sheet

def add_data_to_google_sheets(name, subject, marks, attendance, study_hours, roll_number):
    sheet = open_sheet("GrowthMindsetData")
    existing_data = sheet.get_all_records()
    if any(str(row['Roll Number']) == str(roll_number) for row in existing_data):
        st.error(f"Student with Roll Number {roll_number} already exists!")
    else:
        sheet.append_row([roll_number, name, subject, marks, attendance, study_hours])
        st.success(f"Data for {name} added to Google Sheets!")

def delete_student_from_google_sheets(roll_number):
    sheet = open_sheet("GrowthMindsetData")
    existing_data = sheet.get_all_records()
    row_to_delete = None
    for idx, row in enumerate(existing_data, start=2):  
        if str(row['Roll Number']) == str(roll_number):
            row_to_delete = idx
            break
    if row_to_delete:
        sheet.delete_rows(row_to_delete)
        st.success(f"Data for student with Roll Number {roll_number} deleted from Google Sheets!")
    else:
        st.error(f"No student found with Roll Number {roll_number}")

def display_leaderboard():
    sheet = open_sheet("GrowthMindsetData")
    data = pd.DataFrame(sheet.get_all_records())
    sorted_data = data.sort_values(by='Marks', ascending=False)
    st.write("### Leaderboard")
    st.dataframe(sorted_data[['Roll Number', 'Student Name', 'Marks']].head(10))

def filter_students():
    sheet = open_sheet("GrowthMindsetData")
    data = pd.DataFrame(sheet.get_all_records())
    roll_number_filter = st.text_input("Search by Roll Number")
    if roll_number_filter:
        filtered_data = data[data['Roll Number'].astype(str).str.contains(roll_number_filter)]
        st.write("### Filtered Students Data")
        st.dataframe(filtered_data)

def show_progress_tracker():
    sheet = open_sheet("GrowthMindsetData")
    data = pd.DataFrame(sheet.get_all_records())
    st.write("### Progress Tracker")
    st.line_chart(data[['Attendance', 'Study Hours']])

def show_subject_performance():
    sheet = open_sheet("GrowthMindsetData")
    data = pd.DataFrame(sheet.get_all_records())
    
    st.write("### Subject Performance Analysis")
    
    subject_avg_marks = data.groupby('Subject')['Marks'].mean().reset_index()
    
    st.write("### Average Marks for Each Subject")
    st.dataframe(subject_avg_marks)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(subject_avg_marks['Subject'], subject_avg_marks['Marks'], color='orange')
    
    ax.set_xlabel('Subjects')
    ax.set_ylabel('Average Marks')
    ax.set_title('Subject Performance Analysis')
    
    st.pyplot(fig)

def show_graph():
    sheet = open_sheet("GrowthMindsetData")
    data = pd.DataFrame(sheet.get_all_records())
    
    st.write("### Student Marks Distribution")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(data['Marks'], bins=20, color='blue', alpha=0.7)
    
    ax.set_xlabel('Marks')
    ax.set_ylabel('Number of Students')
    ax.set_title('Marks Distribution')
    
    st.pyplot(fig)

def gamification(marks):
    reward_thresholds = {
        90: "Gold Medal 🥇",
        80: "Silver Medal 🥈",
        70: "Bronze Medal 🥉",
        60: "Great Effort 🌟",
        50: "Keep Trying 💪",
    }
    
    reward = "Better luck next time! 🎯"
    for threshold in reward_thresholds:
        if marks >= threshold:
            reward = reward_thresholds[threshold]
            break
    
    return reward

st.title("Student Performance Analyzer 📊")
st.markdown("""
    <h2 style="text-align: center; color: #2A4D5B;">Track, Analyze, and Manage Student Performance Efficiently</h2>
    <p style="text-align: center; color: #5A6A73;">Upload data, track progress, and get insights with ease!</p>
""", unsafe_allow_html=True)

st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose functionality", ["Home", "Add/Delete Student", "Leaderboard", "Filter Students", "Progress Tracker", "Graphs", "Subject Performance"])

if app_mode == "Home":
    st.markdown("### Instructions")
    st.write("1. Upload a CSV file to add students to the system.")
    st.write("2. View and analyze student performance data.")
    st.write("3. Add or delete student information directly.")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        st.write("### Uploaded Data")
        st.dataframe(data)

        required_columns = {'Roll Number', 'Student Name', 'Subject', 'Marks', 'Attendance', 'Study Hours'}
        if required_columns.issubset(data.columns):
            for index, row in data.iterrows():
                roll_number = row['Roll Number']
                name = row['Student Name']
                subject = row['Subject']
                marks = row['Marks']
                attendance = row['Attendance']
                study_hours = row['Study Hours']
                add_data_to_google_sheets(name, subject, marks, attendance, study_hours, roll_number)
            
            st.write("### Students Data")
            sheet = open_sheet("GrowthMindsetData")
            students_data = pd.DataFrame(sheet.get_all_records())
            st.dataframe(students_data)
        else:
            missing_columns = required_columns - set(data.columns)
            st.error(f"CSV file is missing the following required columns: {', '.join(missing_columns)}")

elif app_mode == "Add/Delete Student":
    st.write("## Add New Student")
    roll_number = st.text_input("Roll Number")
    name = st.text_input("Student Name")
    subject = st.text_input("Subject")
    marks = st.number_input("Marks", min_value=0, max_value=100)
    attendance = st.number_input("Attendance", min_value=0, max_value=100)
    study_hours = st.number_input("Study Hours", min_value=0)
    submit_button = st.button("Add Student")
    if submit_button:
        add_data_to_google_sheets(name, subject, marks, attendance, study_hours, roll_number)
        reward = gamification(marks)
        st.success(f"Student added! {reward}")

    st.write("## Delete Student")
    roll_number_to_delete = st.text_input("Enter Roll Number to Delete")

    if st.button("Delete Student"):
     if roll_number_to_delete.strip(): 
        success = delete_student_from_google_sheets(roll_number_to_delete)
        if success:
            st.success(f"Student with Roll Number {roll_number_to_delete} has been deleted.")
        else:
            st.error("Roll Number not found. Please enter a valid Roll Number.")
    else:
        st.warning("Please enter a valid Roll Number.") 




elif app_mode == "Leaderboard":
    display_leaderboard()

elif app_mode == "Filter Students":
    filter_students()

elif app_mode == "Progress Tracker":
    show_progress_tracker()

elif app_mode == "Graphs":
    show_graph()

elif app_mode == "Subject Performance":
    show_subject_performance()
