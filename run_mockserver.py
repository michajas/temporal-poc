import time
import random
import uvicorn
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from pydantic import BaseModel

# --- Configuration ---

# Global Chaos Settings (can be overridden per endpoint)
CHAOS_CONFIG = {
    "default": {
        "delay_seconds": 0,  # Average delay in seconds
        "error_rate": 0.0,  # Percentage (0.0 to 1.0) of requests to fail
        "error_codes": [500, 502], # Possible error codes to return
    },
    "/dummy": { # Example endpoint-specific config
        "delay_seconds": 0.5,
        "error_rate": 0.1, # 10% error rate for /dummy
        "error_codes": [500],
    },
    # Add more endpoint-specific configs here:
    "/authorize_payment": {
        "delay_seconds": 0.2,
        "error_rate": 0.05, # 5% error rate
        "error_codes": [500, 503],
    },
    "/verify_wallet": {
        "delay_seconds": 0.1,
        "error_rate": 0.15, # 15% error rate
        "error_codes": [500],
    },
    "/send_crypto": {
        "delay_seconds": 1.0, # Simulate a slower operation
        "error_rate": 0.08, # 8% error rate
        "error_codes": [502, 504],
    },
}

# --- Chaos Middleware ---

class ChaosMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        endpoint_path = request.url.path
        config = CHAOS_CONFIG.get(endpoint_path, CHAOS_CONFIG.get("default", {}))

        delay = config.get("delay_seconds", 0)
        error_rate = config.get("error_rate", 0.0)
        error_codes = config.get("error_codes", [500])

        # Simulate delay
        if delay > 0:
            await asyncio.sleep(delay) # Use asyncio.sleep for non-blocking delay

        # Simulate errors
        if error_rate > 0 and random.random() < error_rate:
            status_code = random.choice(error_codes)
            return JSONResponse(
                status_code=status_code,
                content={"detail": f"Chaos Engineering: Simulated {status_code} error"}
            )

        # Proceed with the actual request handling if no chaos induced
        response = await call_next(request)
        return response

# --- FastAPI App ---

# Pydantic model for request body
class PaymentAuthRequest(BaseModel):
    card_number: str
    reference_id: str

# Pydantic model for wallet verification request body
class WalletVerifyRequest(BaseModel):
    wallet_id: str
    reference_id: str

# Pydantic model for crypto send request body
class CryptoSendRequest(BaseModel):
    source_wallet_id: str
    dest_wallet_id: str
    reference_id: str

app = FastAPI()

# Add the middleware
# Need to import asyncio first
app.add_middleware(ChaosMiddleware)

@app.get("/dummy")
async def read_dummy():
    """
    A simple dummy endpoint.
    """
    return {"message": "This is a dummy response."}

# Add other endpoints here later

@app.post("/authorize_payment")
async def authorize_payment(payment_request: PaymentAuthRequest):
    """
    Authorizes a payment based on card number and reference ID.
    Randomly returns a 400 error 20% of the time.
    """
    if random.random() < 0.2: # 20% chance of 400 error
        raise HTTPException(status_code=400, detail="Simulated Bad Request")

    # Simulate successful authorization
    return {
        "status": "authorized",
        "reference_id": payment_request.reference_id
    }

@app.post("/verify_wallet")
async def verify_wallet(verify_request: WalletVerifyRequest):
    """
    Verifies a wallet based on wallet_id and reference_id.
    Randomly returns a 400 error 20% of the time.
    """
    if random.random() < 0.2: # 20% chance of 400 error
        raise HTTPException(status_code=400, detail="Simulated Bad Request for Wallet Verification")

    # Simulate successful verification
    return {
        "status": "verified",
        "reference_id": verify_request.reference_id
    }

@app.post("/send_crypto")
async def send_crypto(send_request: CryptoSendRequest):
    """
    Sends crypto from source to destination wallet.
    Randomly returns a 400 error 20% of the time.
    """
    if random.random() < 0.2: # 20% chance of 400 error
        raise HTTPException(status_code=400, detail="Simulated Bad Request for Crypto Send")

    # Simulate successful crypto send
    # In a real scenario, you might check balances, etc.
    return {
        "status": "sent",
        "transaction_id": f"txn_{random.randint(1000, 9999)}", # Example transaction ID
        "reference_id": send_request.reference_id
    }

# --- Run Server ---

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
