from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import json

# Replace with your own client ID and client secret
CLIENT_CONFIG = {
    "installed": {
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}

# Set up the OAuth 2.0 flow
flow = Flow.from_client_config(
    CLIENT_CONFIG,
    scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
)

# Tell the user to go to the authorization URL
auth_url, _ = flow.authorization_url(prompt='consent')
print(f'Please go to this URL and authorize the application: {auth_url}')

# Get the authorization code from the user
code = input('Enter the authorization code: ')

# Exchange the authorization code for credentials
flow.fetch_token(code=code)

# Get the credentials
credentials = flow.credentials

# Save the credentials to token.json
token_data = {
    'token': credentials.token,
    'refresh_token': credentials.refresh_token,
    'token_uri': credentials.token_uri,
    'client_id': credentials.client_id,
    'client_secret': credentials.client_secret,
    'scopes': credentials.scopes
}

with open('token.json', 'w') as token_file:
    json.dump(token_data, token_file)

print('Token has been saved to token.json')