# Event Registration Tracker

This application tracks event registrations over time from a Google Sheet.

## Environment Setup

This application uses environment variables for configuration. Create a `.env` file in the root directory with the following variables:

SERVICE_ACCOUNT_FILE=
SPREADSHEET_ID=
RANGE_NAME=

## Installation

```bash
# Install dependencies
poetry install

# Run the application
poetry run streamlit run app.py
```

## Security Notes

- Never commit your `.env` file to version control
- Make sure to add `.env` to your `.gitignore` file
- Keep your Google API credentials secure
