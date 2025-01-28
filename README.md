# Nordigen Bank Account Manager

A command-line interface (CLI) tool for managing bank account connections and retrieving financial data using the Nordigen (GoCardless) API.

## Features

- 🏦 Browse and connect to banks by country
- 💰 Check account balances
- 📊 View and download transactions
- 🔄 Automatic token management
- 📥 Bulk transaction export to CSV
- 🌍 Multi-country support
- 🔐 Secure credential management

## Prerequisites

- Python 3.6 or higher
- Nordigen API credentials (Secret ID and Secret Key)
- Internet connection

## Installation

1. Clone this repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your Nordigen credentials:
```plaintext
NORDIGEN_SECRET_ID=your_secret_id
NORDIGEN_SECRET_KEY=your_secret_key
```

## Initial Setup

Generate initial access tokens by running:
```bash
python generate_token.py
```

## Usage

### Browse and Connect to Banks
```bash
python cli-tool-version.py browse-banks --country IT
```

### Check Account Balances
```bash
python cli-tool-version.py check-balances --bank-id BANK_ID
```

### View Transactions
```bash
python cli-tool-version.py check-transactions --bank-id BANK_ID
```
