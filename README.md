# GoCardless Bank Account Manager

A command-line interface (CLI) tool for managing bank account connections and retrieving financial data using the GoCardless (formerly Nordigen) Bank Account Data API.

## Features

- 🏦 Browse and connect to banks by country
- 💰 Check account balances
- 📊 View and download transactions
- 🔄 Automatic token management
- 📥 Bulk transaction export to CSV
- 📥 Bulk transaction convert to CSV
- 🌍 Multi-country support
- 🔐 Secure credential management

## Prerequisites

- Python 3.6 or higher
- GoCardless Bank Account Data API credentials (Secret ID and Secret Key)
- Internet connection

## Installation

1. Clone this repository:
```bash
git clone https://github.com/thetombrider/gocardlessconnection
cd gocardlessconnection
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your GoCardless credentials:
```plaintext
GOCARDLESS_SECRET_ID=your_secret_id
GOCARDLESS_SECRET_KEY=your_secret_key
```

## Initial Setup

Generate initial access tokens by running:
```bash
python generate_token.py
```

## Usage

### Browse and Connect to Banks
```bash
python connector.py browse-banks --country IT
```

### Check Account Balances
```bash
python connector.py check-balances --bank-id BANK_ID
```

### View Transactions
```bash
python connector.py check-transactions --bank-id BANK_ID
```

### Export Transactions to CSV
```bash
python connector.py export-transactions --bank-id BANK_ID
```

### Convert Transactions to CSV
```bash
python connector.py convert-transactions --bank-id BANK_ID
```


first release 31/01/2025