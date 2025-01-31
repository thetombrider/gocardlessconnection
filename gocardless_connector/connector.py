import os
from dotenv import load_dotenv, set_key
from nordigen import NordigenClient
from uuid import uuid4
import click
import csv
from datetime import datetime
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize GoCardless client
client = NordigenClient(
    secret_id=os.getenv('GOCARDLESS_SECRET_ID'),
    secret_key=os.getenv('GOCARDLESS_SECRET_KEY')
)

def generate_new_tokens():
    """
    Comprehensive token generation process with detailed error handling and logging.
    """
    # Try multiple locations for .env file
    env_locations = [
        os.path.join(os.getcwd(), '.env'),  # Current working directory
        os.path.join(os.path.dirname(__file__), '.env'),  # Package directory
    ]
    
    env_loaded = False
    for env_path in env_locations:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            env_loaded = True
            break
    
    if not env_loaded:
        raise ValueError("""
        ❌ .env file not found!
        Please create a .env file in your current directory with:
        GOCARDLESS_SECRET_ID=your_actual_secret_id
        GOCARDLESS_SECRET_KEY=your_actual_secret_key
        """)

    # Retrieve secret credentials
    SECRET_ID = os.getenv('GOCARDLESS_SECRET_ID')
    SECRET_KEY = os.getenv('GOCARDLESS_SECRET_KEY')

    # Validate credentials
    if not SECRET_ID or not SECRET_KEY:
        raise ValueError("""
        ❌ Missing GoCardless Credentials
        Please ensure your .env file contains:
        GOCARDLESS_SECRET_ID=your_actual_secret_id
        GOCARDLESS_SECRET_KEY=your_actual_secret_key
        
        How to obtain these:
        1. Sign up at GoCardless Bank Account Data API
        2. Navigate to API credentials section
        3. Generate new Secret ID and Secret Key
        """)

    try:
        # Initialize GoCardless client
        client = NordigenClient(
            secret_id=SECRET_ID,
            secret_key=SECRET_KEY
        )

        # Generate new tokens
        token_data = client.generate_token()

        # Verify token generation
        if not token_data or 'access' not in token_data or 'refresh' not in token_data:
            raise ValueError("Token generation failed. Incomplete token data.")

        # Get path to .env file
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

        # Update .env with new tokens
        set_key(dotenv_path, 'GOCARDLESS_ACCESS_TOKEN', token_data['access'])
        set_key(dotenv_path, 'GOCARDLESS_REFRESH_TOKEN', token_data['refresh'])

        print("🔑 New Tokens Generated Successfully:")
        print(f"Access Token (first 10 chars): {token_data['access'][:10]}...")
        print(f"Refresh Token (first 10 chars): {token_data['refresh'][:10]}...")
        
        return client, token_data

    except Exception as e:
        print(f"\n❌ Token Generation Error: {e}")
        print("\nPossible Reasons:")
        print("1. Network connectivity issues")
        print("2. Invalid GoCardless credentials")
        print("3. GoCardless API temporary unavailability")
        print("\nRecommended Actions:")
        print("- Check your internet connection")
        print("- Verify your GoCardless account credentials")
        print("- Contact GoCardless support if issue persists")
        raise

def refresh_access_token(client, refresh_token):
    """
    Enhanced token refresh with comprehensive error handling and diagnostics.
    """
    try:
        # Validate refresh token
        if not refresh_token:
            raise ValueError("No refresh token provided")

        # Attempt token exchange
        new_token_data = client.exchange_token(refresh_token)

        # Validate returned token data
        if not new_token_data or 'access' not in new_token_data:
            raise ValueError("Token exchange returned invalid data")

        # Update client token
        client.token = new_token_data['access']

        # Update .env file
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        set_key(dotenv_path, 'GOCARDLESS_ACCESS_TOKEN', new_token_data['access'])
        
        # Only update refresh token if a new one was provided
        if 'refresh' in new_token_data:
            set_key(dotenv_path, 'GOCARDLESS_REFRESH_TOKEN', new_token_data['refresh'])

        print("✅ Access Token Refreshed Successfully")
        return new_token_data

    except Exception as e:
        print(f"\n❌ Token Refresh Error: {e}")
        print("\nDetailed Diagnostics:")
        print("1. Current refresh token might be expired")
        print("2. GoCardless API authentication requirements may have changed")
        print("3. Network or connectivity issues")
        
        # Instead of generating new tokens here, raise the exception
        raise

def validate_tokens():
    """
    Validate the access and refresh tokens. If the access token is missing or invalid,
    generate new tokens or refresh the existing ones.
    Returns the updated client instance.
    """
    global client
    
    # Load environment variables to ensure we have the latest tokens
    load_dotenv()
    
    refresh_token = os.getenv('GOCARDLESS_REFRESH_TOKEN')
    access_token = os.getenv('GOCARDLESS_ACCESS_TOKEN')
    secret_id = os.getenv('GOCARDLESS_SECRET_ID')
    secret_key = os.getenv('GOCARDLESS_SECRET_KEY')

    # Reinitialize client with secret credentials
    client = NordigenClient(
        secret_id=secret_id,
        secret_key=secret_key
    )

    try:
        if not access_token:
            print("❌ No access token found. Generating new tokens...")
            client, token_data = generate_new_tokens()
        else:
            try:
                token_data = refresh_access_token(client, refresh_token)
            except Exception as e:
                print("🔄 Token refresh failed, generating new tokens...")
                client, token_data = generate_new_tokens()
        
        # Ensure client has the latest token
        client.token = token_data['access']
        return client
        
    except Exception as e:
        print(f"❌ Token validation error: {e}")
        raise

def get_bank_transactions(account, start_date=None, end_date=None):
    """
    Retrieve transactions for a specific account.
    """
    try:
        transactions = account.get_transactions()
        if not isinstance(transactions, dict) or 'transactions' not in transactions:
            print("No transaction data available")
            return
        
        booked = transactions.get('transactions', {}).get('booked', [])
        pending = transactions.get('transactions', {}).get('pending', [])
        
        print("\n📊 Transactions:")
        print("-" * 50)
        
        if booked:
            print("\nBooked Transactions:")
            for tx in booked:
                date = tx.get('bookingDate', 'Unknown date')
                amount = tx.get('transactionAmount', {}).get('amount', 'Unknown amount')
                currency = tx.get('transactionAmount', {}).get('currency', '')
                description = tx.get('remittanceInformationUnstructured', 'No description')
                
                print(f"\nDate: {date}")
                print(f"Amount: {amount} {currency}")
                print(f"Description: {description}")
                print("-" * 30)
        
        if pending:
            print("\nPending Transactions:")
            for tx in pending:
                # Similar structure as booked transactions
                print(f"Amount: {tx.get('transactionAmount', {}).get('amount')} {tx.get('transactionAmount', {}).get('currency')}")
                print(f"Description: {tx.get('remittanceInformationUnstructured', 'No description')}")
                print("-" * 30)
                
    except Exception as e:
        print(f"Error retrieving transactions: {e}")

def handle_bank_account_options(account):
    """
    Handle options for a specific bank account.
    """
    while True:
        print("\n🏦 Account Options:")
        print("1. Check Balance")
        print("2. Download Transactions")
        print("3. Go Back")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            balances = account.get_balances()
            if isinstance(balances, dict) and 'balances' in balances:
                print("\n💰 Current Balances:")
                for balance in balances['balances']:
                    balance_type = balance.get('balanceType', 'Unknown')
                    amount = balance.get('balanceAmount', {}).get('amount')
                    currency = balance.get('balanceAmount', {}).get('currency')
                    last_change = balance.get('lastChangeDateTime', 'Unknown')
                    print(f"\nType: {balance_type}")
                    print(f"Amount: {amount} {currency}")
                    print(f"Last Updated: {last_change}")
            else:
                print("Balance information not available")
                
        elif choice == "2":
            get_bank_transactions(account)
            
        elif choice == "3":
            break
            
        else:
            print("Invalid choice. Please try again.")

def select_institution(institutions):
    """
    Enhanced institution selection with direct ID input option.
    """
    while True:
        print("\n🏦 Bank Selection Options:")
        print("1. List All Banks")
        print("2. Search by Name")
        print("3. Filter by Country")
        print("4. Enter Bank ID Directly")
        print("5. Go Back")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "4":
            bank_id = input("Enter the bank ID: ")
            # Find bank by ID
            matching_bank = next((bank for bank in institutions if bank['id'] == bank_id), None)
            if matching_bank:
                return matching_bank
            else:
                print("❌ Bank ID not found")
                continue
        
        elif choice == "1":
            # List All Banks
            display_institutions(institutions)
        
        elif choice == '2':
            # Search by Name
            search_term = input("\nEnter bank name or partial name: ").lower()
            matching_banks = [
                bank for bank in institutions 
                if search_term in bank['name'].lower()
            ]
            
            display_institutions(matching_banks)
        
        elif choice == '3':
            # Filter by Country
            country = input("Enter country code (e.g., IT for Italy): ").upper()
            country_banks = [
                bank for bank in institutions 
                if country in bank.get('countries', [])  # Changed to check countries array
            ]
            
            display_institutions(country_banks)
        
        elif choice == '5':
            print("Exiting bank selection.")
            return None
        
        else:
            print("Invalid choice. Please try again.")
            continue
        
        # Confirmation of bank selection
        bank_index = input("\nEnter the number of your bank (or 0 to go back): ")
        
        try:
            bank_index = int(bank_index)
            
            if bank_index == 0:
                continue
            
            if 1 <= bank_index <= len(matching_banks):
                selected_bank = matching_banks[bank_index - 1]
                
                # Updated confirmation display
                print("\n✅ Selected Bank:")
                print(f"Name: {selected_bank['name']}")
                print(f"ID: {selected_bank['id']}")
                print(f"Country: {selected_bank.get('countries', ['Unknown'])[0]}")
                
                confirm = input("\nConfirm selection? (y/n): ").lower()
                
                if confirm == 'y':
                    return selected_bank
            else:
                print("Invalid bank number. Please try again.")
        
        except ValueError:
            print("Please enter a valid number.")

def display_institutions(banks, max_display=20):
    """
    Displays institutions in a paginated, user-friendly format.
    """
    if not banks:
        print("No banks found matching your criteria.")
        return
    
    # Sort banks alphabetically by name
    sorted_banks = sorted(banks, key=lambda x: x.get('name', ''))
    
    print("\n🏦 Available Banks:")
    print("-" * 50)
    
    for idx, bank in enumerate(sorted_banks, 1):
        name = bank.get('name', 'Unknown Bank')
        country_code = bank.get('countries', ['Unknown'])[0]
        
        print(f"{idx}. {name} (Country: {country_code})")
        
        if idx % max_display == 0 and idx < len(sorted_banks):
            input("\nPress Enter for more results...")

def display_accounts(accounts_info):
    """
    Display all accounts and let user select one.
    """
    print("\n📊 Available Accounts:")
    print("-" * 50)
    
    for idx, acc in enumerate(accounts_info, 1):
        print(f"{idx}. {acc['name']} - {acc['product']}")
        print(f"   IBAN: {acc['iban']}")
        print(f"   Currency: {acc['currency']}")
        print("-" * 30)
    
    while True:
        try:
            choice = input("\nSelect account number (or 0 to exit): ")
            choice = int(choice)
            
            if choice == 0:
                return None
            
            if 1 <= choice <= len(accounts_info):
                return accounts_info[choice - 1]
            
            print("Invalid account number. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def get_bank_accounts(client, institution):
    """
    Modified to handle account selection and operations with better error handling.
    """
    try:
        # Check for existing requisition ID for this institution
        load_dotenv()
        stored_req_id = os.getenv(f'REQUISITION_ID_{institution["id"]}')
        requisition = None
        
        if stored_req_id:
            print("\n🔄 Found existing authorization, attempting to reuse...")
            try:
                requisition = client.requisition.get_requisition_by_id(
                    requisition_id=stored_req_id
                )
                if requisition.get('status', '') != 'LN':
                    print("❌ Existing authorization has expired")
                    stored_req_id = None
                    # Remove invalid requisition ID from .env
                    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
                    set_key(dotenv_path, f'REQUISITION_ID_{institution["id"]}', '')
                else:
                    print("✅ Successfully reused existing authorization")
            except Exception as e:
                print(f"❌ Error with stored authorization: {e}")
                stored_req_id = None
                # Remove invalid requisition ID from .env
                dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
                set_key(dotenv_path, f'REQUISITION_ID_{institution["id"]}', '')
                
        if not stored_req_id:
            # Initialize new session with the bank
            init = client.initialize_session(
                institution_id=institution['id'],
                redirect_uri="https://gocardless.com",
                reference_id=str(uuid4())
            )
            
            print("\n🔐 Bank Authorization Required")
            print("Please complete these steps:")
            print("1. Visit this link in your browser:")
            print(f"\n{init.link}\n")
            print("2. Log in to your bank account")
            print("3. Authorize access to your account data")
            print("4. You will be redirected to gocardless.com - this is expected")
            
            input("\nPress Enter after completing the authorization process...")
            
            requisition = client.requisition.get_requisition_by_id(
                requisition_id=init.requisition_id
            )
            
            # Store successful requisition ID
            if requisition.get('status', '') == 'LN':
                dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
                set_key(dotenv_path, f'REQUISITION_ID_{institution["id"]}', init.requisition_id)
            else:
                print("❌ Authorization failed or incomplete")
                return None

        if not requisition or not requisition.get('accounts', []):
            print("❌ No accounts found. Authorization might not be completed.")
            return None
        
        accounts_info = []
        for account_id in requisition['accounts']:
            try:
                account = client.account_api(account_id)
                details = account.get_details()
                account_info = details.get('account', {})
                
                accounts_info.append({
                    'id': account_id,
                    'name': account_info.get('ownerName', 'Unknown'),
                    'iban': account_info.get('iban', 'Not available'),
                    'currency': account_info.get('currency', 'Unknown'),
                    'product': account_info.get('product', ''),
                    'account_api': account
                })
                
            except Exception as e:
                print(f"Error processing account {account_id}: {str(e)}")
                continue
        
        while True:
            selected_account = display_accounts(accounts_info)
            if not selected_account:
                break
                
            handle_bank_account_options(selected_account['account_api'])
                
    except Exception as e:
        print(f"\n❌ Error retrieving accounts: {e}")

def list_connected_banks():
    """
    List bank IDs of banks to which the user has connected already.
    """
    print("\n📋 Connected Banks:")
    print("-" * 50)
    
    # Assuming bank IDs are stored in the .env file with a specific prefix
    connected_banks = {key: value for key, value in os.environ.items() if key.startswith('REQUISITION_ID_')}
    
    if not connected_banks:
        print("❌ No connected banks found.")
        return
    
    for bank_id, requisition_id in connected_banks.items():
        print(f"Bank ID: {bank_id.split('_')[-1]}, Requisition ID: {requisition_id}")

def get_all_bank_transactions():
    """
    Get transactions from all connected banks automatically without user interaction.
    """
    transactions = []
    connected_banks = {key: value for key, value in os.environ.items() if key.startswith('REQUISITION_ID_')}
    
    if not connected_banks:
        print("❌ No connected banks found.")
        return transactions

    for bank_env_key, requisition_id in connected_banks.items():
        try:
            bank_id = bank_env_key.replace('REQUISITION_ID_', '')
            institution = client.institution.get_institution_by_id(bank_id)
            
            if not institution:
                print(f"❌ Bank {bank_id} not found")
                continue

            # Get accounts directly from requisition
            try:
                requisition = client.requisition.get_requisition_by_id(requisition_id)
                if requisition.get('status', '') != 'LN':
                    print(f"❌ Authorization expired for bank {institution['name']}")
                    continue
                
                for account_id in requisition['accounts']:
                    try:
                        account = client.account_api(account_id)
                        details = account.get_details()
                        account_info = details.get('account', {})
                        
                        # Get transactions for this account
                        transactions_data = account.get_transactions()
                        if isinstance(transactions_data, dict) and 'transactions' in transactions_data:
                            for trans_type, trans_list in transactions_data['transactions'].items():
                                for transaction in trans_list:
                                    formatted_transaction = {
                                        'bank_name': institution['name'],
                                        'account_iban': account_info.get('iban', 'Not available'),
                                        'transaction_id': transaction.get('transactionId', ''),
                                        'booking_date': transaction.get('bookingDate', ''),
                                        'amount': transaction.get('transactionAmount', {}).get('amount', ''),
                                        'currency': transaction.get('transactionAmount', {}).get('currency', ''),
                                        'description': transaction.get('remittanceInformationUnstructured', '')
                                    }
                                    transactions.append(formatted_transaction)
                        
                    except Exception as e:
                        print(f"Error processing account {account_id}: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error processing bank {institution['name']}: {str(e)}")
                continue

        except Exception as e:
            print(f"Error processing bank {bank_id}: {str(e)}")
            continue

    return transactions

@click.group()
def cli():
    """Main CLI for Nordigen Bank Account Management."""
    pass

@cli.command()
@click.option('--country', default='IT', help='Country code for bank institutions')
def browse_banks(country):
    """Browse and connect to banks."""
    print("\n🌐 Ready to interact with Nordigen API")
    
    # Validate tokens before proceeding
    validate_tokens()

    while True:
        try:
            banks = client.institution.get_institutions(country)
            print(f"\n🏦 Retrieved {len(banks)} {country} banks")
            
            selected_bank = select_institution(banks)
            
            if selected_bank:
                get_bank_accounts(client, selected_bank)
            else:
                print("\nThank you for using the Bank Account Manager!")
                break
                
        except Exception as e:
            print(f"❌ Error: {e}")
            choice = input("\nWould you like to try again? (y/n): ").lower()
            if choice != 'y':
                break

@cli.command()
@click.option('--bank-id', required=True, help='ID of the bank to check balances for')
def check_balances(bank_id):
    """Check balances for accounts at specified bank."""
    # Validate tokens before proceeding
    validate_tokens()

    try:
        # First, verify if this bank ID exists
        try:
            institution = client.institution.get_institution_by_id(bank_id)
        except Exception as e:
            print(f"\n❌ Bank ID '{bank_id}' not found.")
            print("\nTo find the correct bank ID:")
            print("1. Use 'gocardless-connector browse-banks' to list available banks")
            print("2. Note the ID of your bank from the list")
            print("3. Try again with the correct bank ID")
            return

        if not institution:
            print("❌ Bank not found.")
            return
        
        print(f"\n✅ Found bank: {institution.get('name', 'Unknown Bank')}")
        accounts_info = get_bank_accounts(client, institution)
        
        if accounts_info:
            for account in accounts_info:
                handle_bank_account_options(account['account_api'])
        else:
            print("❌ No accounts found for this bank.")
            
    except Exception as e:
        print(f"❌ Error retrieving balances: {e}")
        print("\nTroubleshooting steps:")
        print("1. Verify your internet connection")
        print("2. Ensure the bank ID is correct")
        print("3. Try browsing banks first using: gocardless-connector browse-banks")

@cli.command()
@click.option('--bank-id', required=True, help='ID of the bank to check transactions for')
def check_transactions(bank_id):
    """Check transactions for accounts at specified bank."""
    # Validate tokens before proceeding
    validate_tokens()

    try:
        institution = client.institution.get_institution_by_id(bank_id)
        if not institution:
            print("❌ Bank not found.")
            return
        
        accounts_info = get_bank_accounts(client, institution)
        if accounts_info:
            for account in accounts_info:
                get_bank_transactions(account['account_api'])
        else:
            print("❌ No accounts found for this bank.")
    except Exception as e:
        print(f"❌ Error retrieving transactions: {e}")

@cli.command()
def list_banks():
    """List bank IDs of banks to which the user has connected already."""
    list_connected_banks()

@cli.command()
@click.option('--output', default='transactions.csv', help='Output CSV file name')
def download_all_transactions(output):
    """Download all transactions from all connected banks into a CSV file."""
    try:
        # Get updated client with valid token
        global client
        client = validate_tokens()
        
        print("\n📥 Fetching transactions from all connected banks...")
        transactions = get_all_bank_transactions()
        
        if not transactions:
            print("❌ No transactions found.")
            return
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(transactions)
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{output.rsplit('.', 1)[0]}_{timestamp}.csv"
        
        df.to_csv(filename, index=False, encoding='utf-8')
        
        print(f"\n✅ Successfully saved {len(transactions)} transactions to {filename}")
        print(f"💡 Transaction summary:")
        print(f"Total banks: {df['bank_name'].nunique()}")
        print(f"Total accounts: {df['account_iban'].nunique()}")
        print(f"Date range: {df['booking_date'].min()} to {df['booking_date'].max()}")
        
    except Exception as e:
        print(f"❌ Error downloading transactions: {e}")

@cli.command()
@click.option('--search', help='Search term to filter banks')
@click.option('--country', help='Country code for bank institutions')
def find_bank_id(search, country):
    """Find bank ID by name or partial name."""
    validate_tokens()
    
    if not country:
        country = input("\nEnter country code (press Enter for IT): ").upper() or 'IT'
    
    try:
        banks = client.institution.get_institutions(country)
        
        if not search:
            search = input("\nEnter bank name or partial name to search: ").strip()
        
        if search:
            matching_banks = [
                bank for bank in banks 
                if search.lower() in bank['name'].lower() 
                and country in bank.get('countries', [])  # Add country filter
            ]
        else:
            matching_banks = [
                bank for bank in banks 
                if country in bank.get('countries', [])  # Add country filter
            ]

        if not matching_banks:
            print(f"❌ No banks found matching '{search}' in {country}")
            return

        print("\n🏦 Matching Banks:")
        print("-" * 50)
        for bank in matching_banks:
            print(f"ID: {bank['id']}")
            print(f"Name: {bank['name']}")
            print(f"Country: {country}")  # Use the selected country
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Error: {e}")

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', default=None, help='Output CSV file name')
def convert_transactions(input_file, output):
    """Convert transactions CSV to Italian format."""
    try:
        # Read the input CSV
        df = pd.read_csv(input_file)
        
        # Create new DataFrame with required schema
        converted_df = pd.DataFrame(columns=[
            'data', 'mese', 'descrizione', 'importo entrata', 
            'importo uscita', 'categoria', 'conto'
        ])
        
        # Convert and populate the new DataFrame
        converted_df['data'] = pd.to_datetime(df['booking_date']).dt.date
        converted_df['mese'] = pd.to_datetime(df['booking_date']).dt.strftime('%B')
        converted_df['descrizione'] = df['description']
        converted_df['conto'] = df['account_iban']
        
        # Initialize categoria as empty
        converted_df['categoria'] = ''
        
        # Convert amount to float and split into inflow/outflow
        amounts = pd.to_numeric(df['amount'], errors='coerce')
        converted_df['importo entrata'] = amounts.where(amounts > 0, '')
        converted_df['importo uscita'] = amounts.where(amounts < 0, '').abs()
        
        # Generate output filename if not provided
        if output is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = os.path.splitext(input_file)[0]
            output = f"{base_name}_converted_{timestamp}.csv"
        
        # Save to CSV
        converted_df.to_csv(output, index=False, encoding='utf-8')
        
        print(f"\n✅ Successfully converted transactions to: {output}")
        print(f"💡 Conversion summary:")
        print(f"Total transactions: {len(converted_df)}")
        print(f"Date range: {converted_df['data'].min()} to {converted_df['data'].max()}")
        print(f"Total accounts: {converted_df['conto'].nunique()}")
        
    except Exception as e:
        print(f"❌ Error converting transactions: {e}")
        print("\nTroubleshooting steps:")
        print("1. Ensure the input file is a valid CSV")
        print("2. Check if the input file has the expected columns")
        print("3. Verify the file path is correct")

if __name__ == "__main__":
    cli()