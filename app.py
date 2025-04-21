import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === SETTINGS ===
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Adjust if your sheet has a different name
RANGE_NAME = os.getenv("RANGE_NAME")

st.set_page_config(page_title="Event Registration Tracker", layout="centered")

# === LOAD DATA FROM GOOGLE SHEET ===


@st.cache_data(show_spinner=True)
def load_data():
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values or len(values) < 2:
        return pd.DataFrame()  # empty

    df = pd.DataFrame(values[1:], columns=values[0])
    df['Submitted at'] = pd.to_datetime(df['Submitted at'], errors='coerce')
    df = df.dropna(subset=['Submitted at'])
    df = df.sort_values('Submitted at').reset_index(drop=True)
    df['Cumulative Registrations'] = range(1, len(df) + 1)
    return df


# === UI ===
st.title("📈 Event Registration Over Time")

df = load_data()

if df.empty:
    st.warning("No data found or failed to load.")
else:
    st.success(f"Loaded {len(df)} registrations.")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['Submitted at'], df['Cumulative Registrations'], marker='o')
    ax.set_xlabel("Time")
    ax.set_ylabel("Cumulative Registrations")
    ax.set_title("Registration Timeline")
    ax.grid(True)

    st.pyplot(fig)

    st.dataframe(df[['Submitted at', 'Cumulative Registrations']])
