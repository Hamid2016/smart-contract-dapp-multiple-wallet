# 🧠 Smart Contract dApp – Multiple Wallet Support

This project is a full-stack decentralized application (dApp) built on Ethereum, designed to support **multiple wallet connections**. It combines a FastAPI backend with a clean HTML/JS frontend and SQLite for lightweight data persistence.

---

## 🚀 Features

- 🔐 Connect and manage multiple Ethereum wallets
- 📄 Submit and track policy claims via smart contracts
- 🧠 FastAPI backend with modular controllers
- 🖼️ Simple frontend with real-time wallet interaction
- 🗃️ SQLite database for storing wallet and policy data

---

## 📁 Project Structure

smart-contract-dapp-multiple-wallet/
│
├── main.py                  # FastAPI entry point and route definitions
├── .env                     # Environment variables (Alchemy URL, contract address, etc.)
├── requirements.txt         # Python dependencies
│
├── db/                      # SQLite database file
│   └── dapp.db              # Main database file
│
├── models/                  # SQLite data models
│   ├── db.py                # Database connection logic
│   ├── wallet.py            # Wallet table and operations
│   └── policy.py            # Policy table and operations
│
├── controllers/             # Business logic layer
│   ├── wallet_controller.py # Wallet-related logic
│   └── policy_controller.py # Policy-related logic
│
├── contracts/               # Smart contract source code
│   └── insurancePaymentAbility.sol  # Solidity contract for insurance logic
│
├── static/                  # Frontend assets
│   ├── index.html           # Homepage
│   ├── claim.html           # Claim submission page
│   ├── css/
│   │   └── claim.css        # Styles for claim page
│   ├── js/
│   │   ├── main.js          # JS for homepage
│   │   └── claim.js         # JS for claim page
│
├── logs/                    # Frontend event logging
│   └── frontend-logs.txt    # Logged user actions

---

## 📦 Getting Started

To set up and run the project locally:

```bash
# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate   # On Windows
source .venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run main.py
python main.py
