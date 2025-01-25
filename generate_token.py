import os
from dotenv import load_dotenv, set_key
from nordigen import NordigenClient

def generate_initial_tokens():
    # Load environment variables
    load_dotenv()

    # Retrieve secret credentials
    SECRET_ID = os.getenv('SECRET_ID')
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Validate credentials
    if not SECRET_ID or not SECRET_KEY:
        raise ValueError("Missing Nordigen SECRET_ID or SECRET_KEY in .env file")

    # Initialize Nordigen client
    client = NordigenClient(
        secret_id=SECRET_ID,
        secret_key=SECRET_KEY
    )

    try:
        # Generate initial tokens
        token_data = client.generate_token()

        # Get path to .env file
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

        # Store tokens in .env file
        set_key(dotenv_path, 'ACCESS_TOKEN', token_data['access'])
        set_key(dotenv_path, 'REFRESH_TOKEN', token_data['refresh'])

        print("Initial tokens generated and stored successfully:")
        print(f"Access Token: {token_data['access'][:10]}...")
        print(f"Refresh Token: {token_data['refresh'][:10]}...")

    except Exception as e:
        print(f"Token generation error: {e}")

if __name__ == "__main__":
    generate_initial_tokens()