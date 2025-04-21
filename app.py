import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import pytz

# === Load environment variables ===
load_dotenv()

# Load individual credentials from .env
SERVICE_ACCOUNT_INFO = {
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
}

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
RANGE_NAME = os.getenv("RANGE_NAME")
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

st.set_page_config(
    page_title="CodeQuest Registration Dashboard", layout="centered")

# === Helpers ===


def localize_and_format_submitted_at(df):
    if 'Submitted at' in df.columns:
        df['Submitted at'] = pd.to_datetime(
            df['Submitted at'], errors='coerce')
        df['Submitted at'] = df['Submitted at'].dt.tz_localize(
            'UTC').dt.tz_convert('Asia/Colombo')
        df['Submitted at (SLT)'] = df['Submitted at'].dt.strftime(
            '%Y-%m-%d %I:%M:%S %p')
        df['Cumulative Registrations'] = range(1, len(df) + 1)
    return df

# === Load Data ===


def load_data():
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=credentials)
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()

    values = result.get('values', [])
    if not values or len(values) < 2:
        return pd.DataFrame()

    df = pd.DataFrame(values[1:], columns=values[0])
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=['Submitted at'])

    df = localize_and_format_submitted_at(df)
    df = df.sort_values('Submitted at').reset_index(drop=True)

    return df


# === UI & Charts ===
st.title("📈 CodeQuest Registration Tracker")

df = load_data()

if df.empty:
    st.warning("No data found or failed to load.")
else:
    st.success(f"✅ Loaded {len(df)} registrations.")

    st.metric("🎯 Total Registered Teams", len(df))

    if 'Submitted at' in df.columns:
        st.subheader("📅 Registration Timeline (SL Time)")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df['Submitted at'], df['Cumulative Registrations'], marker='o')
        ax.set_xlabel("Time")
        ax.set_ylabel("Cumulative Registrations")
        ax.set_title("Registrations Over Time (Sri Lanka Time)")
        ax.grid(True)
        st.pyplot(fig)

    if 'Number of Team Members' in df.columns:
        st.subheader("👥 Team Size Distribution")
        team_size_counts = df['Number of Team Members'].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(team_size_counts, labels=team_size_counts.index,
                autopct='%1.1f%%', startangle=140)
        ax2.set_title("Team Sizes")
        st.pyplot(fig2)

    if 'University' in df.columns:
        st.subheader("🏫 University Participation")
        university_counts = df['University'].value_counts()
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        ax3.bar(university_counts.index,
                university_counts.values, color='green')
        ax3.set_xlabel("University")
        ax3.set_ylabel("Team Count")
        ax3.set_title("Universities Represented")
        ax3.tick_params(axis='x', rotation=45)
        st.pyplot(fig3)
