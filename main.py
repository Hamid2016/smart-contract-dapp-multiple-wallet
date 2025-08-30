from fastapi import FastAPI, HTTPException, Request,Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from web3 import Web3, HTTPProvider
from datetime import datetime, timezone
import aiofiles
import os
import json

# Controllers
from controllers.wallet_controller import WalletController
from controllers.policy_controller import PolicyController
from controllers.user_controller import UserController


# Initialize controllers
wallet_controller = WalletController()
policy_controller = PolicyController()
user_controller = UserController()


# Logging setup
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "frontend-logs.txt")
os.makedirs(LOG_DIR, exist_ok=True)
print("🧭 Final log path:", os.path.abspath(LOG_FILE))

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Web3
web3 = Web3(HTTPProvider(os.getenv("ALCHEMY_URL")))
if not web3.is_connected():
    raise ConnectionError("❌ Failed to connect to Ethereum network")

# Contract setup
contract_address = os.getenv("CONTRACT_ADDRESS")
contract_abi = json.loads(os.getenv("CONTRACT_ABI"))
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Model for user loging logout register
class AuthData(BaseModel):
    username: str
    password: str

# claim data model
class ClaimData(BaseModel):
    policy_name: str
    coverage: str
    premium: str
    status: bool

# Request models
class WalletData(BaseModel):
    address: str
    signature: str

class PolicyData(BaseModel):
    address: str
    policy_name: str
    premium: float
    coverage_amount: float

class GetPolicyData(BaseModel):
    address: str

class FrontendLog(BaseModel):
    event: str
    message: str

# Serve homepage
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)

# Connect wallet
@app.post("/connect-wallet")
async def connect_wallet(data: WalletData):
    try:
        connected_address = Web3.to_checksum_address(data.address)
        if not connected_address or not data.signature:
            raise HTTPException(status_code=400, detail="Invalid wallet data")
        wallet_controller.connect_wallet(connected_address)
        return {"message": "Wallet connected and saved!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create policy
@app.post("/create-policy")
async def create_policy(data: PolicyData):
    try:
        connected_address = Web3.to_checksum_address(data.address)
        policy_controller.create_policy(
            connected_address,
            data.policy_name,
            data.premium,
            data.coverage_amount
        )

        premium_wei = web3.to_wei(data.premium, "ether")
        coverage_wei = web3.to_wei(data.coverage_amount, "ether")

        unsigned_tx = contract.functions.createPolicy(
            data.policy_name,
            premium_wei,
            coverage_wei
        ).build_transaction({
            'chainId': web3.eth.chain_id,
            'from': connected_address,
            'nonce': web3.eth.get_transaction_count(connected_address),
            'gas': 300000,
            'maxFeePerGas': web3.to_wei(50, 'gwei'),
            'maxPriorityFeePerGas': web3.to_wei(1, 'gwei'),
            'value': premium_wei
        })

        return {**unsigned_tx, 'to': contract_address}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Get policies from smart contract
@app.post("/get-policies")
async def get_policies(data: GetPolicyData):
    try:
        connected_address = Web3.to_checksum_address(data.address)
        policies = contract.functions.getPolicies().call({"from": connected_address})
        result = [
            {
                "policyName": policy[0],
                "premium": str(policy[1]),
                "coverageAmount": str(policy[2]),
                "isActive": policy[3],
            }
            for policy in policies
        ]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Claim redirect with cookie
@app.get("/claim/{policy_name}")
async def claim_redirect(
    policy_name: str,
    data: ClaimData = Depends()
):
    # Override the model's policy_name with the path param
    data.policy_name = policy_name

    response = RedirectResponse(url="/static/claim.html")
    response.set_cookie(
        key="policy_data",
        value=data.json(),
        httponly=True,
        secure=False,
        samesite="lax"
    )
    return response
# Fetch policy data from cookie
@app.post("/get-policy-data")
async def get_policy_data(request: Request):
    policy_data = request.cookies.get("policy_data")
    if not policy_data:
        raise HTTPException(status_code=404, detail="Policy data not found")
    return JSONResponse(json.loads(policy_data))

# Log frontend events
@app.post("/frontend-log")
async def log_frontend_event(entry: FrontendLog):
    timestamp = datetime.now(timezone.utc).isoformat()
    log_line = f"{timestamp} [{entry.event}] {entry.message}\n"
    try:
        async with aiofiles.open(LOG_FILE, mode="a") as f:
            await f.write(log_line)
        return {"status": "success", "alert": entry.message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logging failed: {str(e)}")

# user endpoints
@app.post("/register")
def register_user(auth_data: AuthData):
    result = user_controller.register(auth_data.username, auth_data.password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/login")
def login_user(auth_data: AuthData):
    result = user_controller.login(auth_data.username, auth_data.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result

@app.post("/logout")
def logout_user(auth_data: AuthData):
    result = user_controller.logout(auth_data.username)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result
# user endpoints

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
