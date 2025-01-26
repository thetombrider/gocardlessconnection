import os
from dotenv import load_dotenv, set_key
from nordigen import NordigenClient
from uuid import uuid4

def generate_new_tokens():
    """
    Comprehensive token generation process with detailed error handling and logging.
    """
    # Load existing environment variables
    load_dotenv()

    # Retrieve secret credentials
    SECRET_ID = os.getenv('NORDIGEN_SECRET_ID')
    SECRET_KEY = os.getenv('NORDIGEN_SECRET_KEY')

    # Validate credentials
    if not SECRET_ID or not SECRET_KEY:
        raise ValueError("""
        ❌ Missing Nordigen Credentials
        Please ensure your .env file contains:
        NORDIGEN_SECRET_ID=your_actual_secret_id
        NORDIGEN_SECRET_KEY=your_actual_secret_key
        
        How to obtain these:
        1. Sign up at Nordigen (https://nordigen.com)
        2. Navigate to API credentials section
        3. Generate new Secret ID and Secret Key
        """)

    try:
        # Initialize Nordigen client
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
        set_key(dotenv_path, 'NORDIGEN_ACCESS_TOKEN', token_data['access'])
        set_key(dotenv_path, 'NORDIGEN_REFRESH_TOKEN', token_data['refresh'])

        print("🔑 New Tokens Generated Successfully:")
        print(f"Access Token (first 10 chars): {token_data['access'][:10]}...")
        print(f"Refresh Token (first 10 chars): {token_data['refresh'][:10]}...")
        
        return client, token_data

    except Exception as e:
        print(f"\n❌ Token Generation Error: {e}")
        print("\nPossible Reasons:")
        print("1. Network connectivity issues")
        print("2. Invalid Nordigen credentials")
        print("3. Nordigen API temporary unavailability")
        print("\nRecommended Actions:")
        print("- Check your internet connection")
        print("- Verify your Nordigen account credentials")
        print("- Contact Nordigen support if issue persists")
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
        set_key(dotenv_path, 'NORDIGEN_ACCESS_TOKEN', new_token_data['access'])
        set_key(dotenv_path, 'NORDIGEN_REFRESH_TOKEN', new_token_data['refresh'])

        print("✅ Access Token Refreshed Successfully")
        return new_token_data

    except Exception as e:
        print(f"\n❌ Token Refresh Error: {e}")
        print("\nDetailed Diagnostics:")
        print("1. Current refresh token might be expired")
        print("2. Nordigen API authentication requirements may have changed")
        print("3. Network or connectivity issues")
        
        # Attempt to generate new tokens
        print("\n🔄 Attempting to generate new tokens...")
        return generate_new_tokens()[1]

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

def handle_bank_account_options(client, account, account_info):
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
    
    Args:
        banks (list): List of financial institutions
        max_display (int): Maximum number of banks to display per page
    """
    if not banks:
        print("No banks found matching your criteria.")
        return
    
    # Sort banks alphabetically by name
    sorted_banks = sorted(banks, key=lambda x: x.get('name', ''))
    
    print("\n🏦 Available Banks:")
    print("-" * 50)
    
    for idx, bank in enumerate(sorted_banks, 1):
        # Safely access bank properties with get() method
        name = bank.get('name', 'Unknown Bank')
        country_code = bank.get('countries', ['Unknown'])[0]  # Nordigen uses 'countries' array
        
        print(f"{idx}. {name} (Country: {country_code})")
        
        # Paginate results
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
    Modified to handle account selection and operations.
    """
    try:
        # Check for existing requisition ID for this institution
        load_dotenv()
        stored_req_id = os.getenv(f'REQUISITION_ID_{institution["id"]}')
        
        if stored_req_id:
            print("\n🔄 Found existing authorization, attempting to reuse...")
            requisition = client.requisition.get_requisition_by_id(
                requisition_id=stored_req_id
            )
            if requisition.get('status', '') == 'LN':
                print("✅ Successfully reused existing authorization")
            else:
                stored_req_id = None
                
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
        
        if not requisition.get('accounts', []):
            print("❌ No accounts found. Authorization might not be completed.")
            return
        
        # Collect all accounts information first
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
                
            while True:
                print(f"\n🏦 Selected Account: {selected_account['name']}")
                print("1. Check Balance")
                print("2. Download Transactions")
                print("3. Select Different Account")
                print("4. Exit")
                
                choice = input("\nEnter your choice (1-4): ")
                
                if choice == "1":
                    balances = selected_account['account_api'].get_balances()
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
                    get_bank_transactions(selected_account['account_api'])
                
                elif choice == "3":
                    break
                
                elif choice == "4":
                    return
                
                else:
                    print("Invalid choice. Please try again.")
                
                input("\nPress Enter to continue...")
                
    except Exception as e:
        print(f"\n❌ Error retrieving accounts: {e}")

def main():
    # Load environment variables
    load_dotenv()

    # Retrieve all credentials
    SECRET_ID = os.getenv('NORDIGEN_SECRET_ID')
    SECRET_KEY = os.getenv('NORDIGEN_SECRET_KEY')
    ACCESS_TOKEN = os.getenv('NORDIGEN_ACCESS_TOKEN')
    REFRESH_TOKEN = os.getenv('NORDIGEN_REFRESH_TOKEN')

    # First, check if we have the basic credentials
    if not all([SECRET_ID, SECRET_KEY]):
        print("❌ Missing SECRET_ID or SECRET_KEY. Please check your .env file.")
        return

    # Initialize client
    client = NordigenClient(
        secret_id=SECRET_ID,
        secret_key=SECRET_KEY
    )

    # Handle token management
    try:
        if not all([ACCESS_TOKEN, REFRESH_TOKEN]):
            print("🔑 No existing tokens found. Generating new ones...")
            client, token_data = generate_new_tokens()
        else:
            # Set the existing access token
            client.token = ACCESS_TOKEN
            try:
                # Try to use existing token by making a test request
                banks = client.institution.get_institutions("IT")
                print("✅ Existing token is valid")
            except Exception:
                print("🔄 Access token expired, attempting refresh...")
                try:
                    token_data = refresh_access_token(client, REFRESH_TOKEN)
                except Exception:
                    print("❌ Token refresh failed. Generating new tokens...")
                    client, token_data = generate_new_tokens()

        print("\n🌐 Ready to interact with Nordigen API")
        
        # Continue with the rest of your code...
        banks = client.institution.get_institutions("IT")
        print(f"\n🏦 Retrieved {len(banks)} Italian banks")
        
        # Let user select a bank
        selected_bank = select_institution(banks)
        
        if selected_bank:
            # Retrieve accounts for the selected bank
            get_bank_accounts(client, selected_bank)
        else:
            print("Bank selection cancelled.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()