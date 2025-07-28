from fastapi import FastAPI, HTTPException
import os
import json
from dotenv import load_dotenv
from web3 import Web3, HTTPProvider
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Add this to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Web3
web3 = Web3(HTTPProvider(os.getenv("ALCHEMY_URL")))


# Verify connection
if not web3.is_connected():
    raise ConnectionError("Failed to connect to Ethereum network")

# Contract setup
contract_address = os.getenv("CONTRACT_ADDRESS")
contract_abi = json.loads(os.getenv("CONTRACT_ABI"))

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Define request models
class WalletData(BaseModel):
    address: str
    signature: str

class PolicyData(BaseModel):
    address: str
    policy_name: str
    premium: float  # Accepting float since frontend sends decimal values
    coverage_amount: float

class GetPolicyData(BaseModel):
    address: str

# Route to serve the frontend
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r" , encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/connect-wallet")
async def connect_wallet(data: WalletData):

    connected_address = data.address
    signature = data.signature

    if not connected_address or not signature:
        raise HTTPException(status_code=400, detail="Invalid wallet data")

    try:
        connected_address = Web3.to_checksum_address(connected_address)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Ethereum address: {str(e)}")

    print(f"Wallet connected: {connected_address}")

    return {"message": "Wallet connected and verified successfully!"}
@app.post("/create-policy")
async def create_policy(data: PolicyData):
    connected_address = data.address
    connected_address = Web3.to_checksum_address(connected_address)

    if not connected_address:
        raise HTTPException(status_code=401, detail="No wallet connected")

    try:
        # Convert ETH values to wei
        premium_wei = web3.to_wei(data.premium, "ether")
        coverage_wei = web3.to_wei(data.coverage_amount, "ether")

        # Build transaction with ETH value
        unsigned_tx = contract.functions.createPolicy(
            data.policy_name,
            premium_wei,
            coverage_wei
        ).build_transaction({
            # 'to': contract_address,
            'chainId': web3.eth.chain_id,
            'from': connected_address,
            'nonce': web3.eth.get_transaction_count(connected_address),
            'gas': 300000,
            'maxFeePerGas': web3.to_wei(50, 'gwei'),
            'maxPriorityFeePerGas': web3.to_wei(1, 'gwei'),
            'value': premium_wei  # This adds ETH transfer to the transaction
        })

        # return unsigned_tx
        # Return complete transaction data including 'to'
        return {
            **unsigned_tx,
            'to': contract_address  # Explicitly include contract address
        }
    except Exception as e:
        raise HTTPException(500, detail=f"Error: {str(e)}")

# Function to get all policies
@app.post("/get-policies")
async def get_policies(data: GetPolicyData):
    try:
        connected_address = data.address
        connected_address = Web3.to_checksum_address(connected_address)
        print(f"Calling getPolicies with address: {connected_address}")
        policies = contract.functions.getPolicies().call({"from": connected_address})
        print(f"Raw contract response: {policies}")

        result = [
            {
                "policyName": policy[0],
                # "premium": policy[1],
                "premium": str(policy[1]),
                # "coverageAmount": policy[2],
                "coverageAmount": str(policy[2]),
                "isActive": policy[3],
            }
            for policy in policies
        ]
        print(f"Formatted response: {result}")
        return result
    except Exception as e:
        print(f"Error in /get-policies: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test3:app", host="0.0.0.0", port=8000)
