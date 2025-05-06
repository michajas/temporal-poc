import httpx
from temporalio import activity
from temporalio.exceptions import ApplicationError

from temporal_poc.shared import TransferDetails

MOCK_SERVER_URL = "http://localhost:8000"  # Assuming mock server runs here

@activity.defn
async def authorize_payment(transfer_details: TransferDetails) -> str:
    """Calls the mock server to authorize payment."""
    activity.logger.info(
        f"Authorizing payment for reference ID: {transfer_details.reference_id}"
    )
    try:
        async with httpx.AsyncClient() as client:
            # Map TransferDetails to the expected PaymentAuthRequest structure
            request_data = {
                "card_number": transfer_details.card_number,
                "reference_id": transfer_details.reference_id,
            }
            response = await client.post(
                f"{MOCK_SERVER_URL}/authorize_payment", # Corrected endpoint
                json=request_data,
            )
            response.raise_for_status()
            result = response.json()
            status = result.get("status", "N/A")
            activity.logger.info(
                f"Payment authorization status '{status}' for reference ID: {transfer_details.reference_id}."
            )
            if status != "authorized":
                 raise ApplicationError(f"Authorization failed with status: {status}", non_retryable=True)
            return status # Return the status upon success
    except httpx.HTTPStatusError as e:
         # Handle HTTP errors (like 4xx from the mock server) specifically
        activity.logger.error(
            f"HTTP error {e.response.status_code} during authorization for reference ID {transfer_details.reference_id}: {e.response.text}"
        )
        # Treat client errors (4xx) as potentially non-retryable application errors
        
        raise ApplicationError(f"Authorization failed: {e.response.text}", non_retryable=False) from e
    except httpx.RequestError as e:
        activity.logger.error(
            f"HTTP request failed during authorization for reference ID {transfer_details.reference_id}: {e!r}"
        )
        # Network errors are typically retryable, but here we mark as non-retryable based on mock setup
        raise ApplicationError(f"Authorization failed: {e}", non_retryable=True) from e
    except Exception as e:
        activity.logger.error(
            f"An unexpected error occurred during authorization for reference ID {transfer_details.reference_id}: {e!r}"
        )
        raise ApplicationError(
            f"Unexpected error during authorization: {e}", non_retryable=True
        ) from e

@activity.defn
async def verify_wallet(transfer_details: TransferDetails) -> str:
    """Calls the mock server to verify the source wallet."""
    activity.logger.info(
        f"Verifying source wallet {transfer_details.source_wallet_id} for reference ID: {transfer_details.reference_id}"
    )
    try:
        async with httpx.AsyncClient() as client:
            # Map TransferDetails to the expected WalletVerifyRequest structure
            request_data = {
                "wallet_id": transfer_details.destination_wallet_id,
                "reference_id": transfer_details.reference_id,
            }
            response = await client.post(
                f"{MOCK_SERVER_URL}/verify_wallet",
                json=request_data,
            )
            response.raise_for_status()
            result = response.json()
            status = result.get("status", "N/A")
            activity.logger.info(
                f"Wallet verification status '{status}' for reference ID: {transfer_details.reference_id}"
            )
            if status != "verified":
                 raise ApplicationError(f"Verification failed with status: {status}", non_retryable=True)
            return status # Return the status upon success
    except httpx.HTTPStatusError as e:
        activity.logger.error(
            f"HTTP error {e.response.status_code} during wallet verification for reference ID {transfer_details.reference_id}: {e.response.text}"
        )
        
        raise ApplicationError(f"Wallet verification failed: {e.response.text}", non_retryable=False) from e
    except httpx.RequestError as e:
        activity.logger.error(
            f"HTTP request failed during wallet verification for reference ID {transfer_details.reference_id}: {e!r}"
        )
        raise ApplicationError(f"Wallet verification failed: {e}", non_retryable=True) from e
    except Exception as e:
        activity.logger.error(
            f"An unexpected error occurred during wallet verification for reference ID {transfer_details.reference_id}: {e!r}"
        )
        raise ApplicationError(
            f"Unexpected error during wallet verification: {e}", non_retryable=True
        ) from e

@activity.defn
async def send_crypto(transfer_details: TransferDetails) -> str:
    """Calls the mock server to send crypto."""
    activity.logger.info(
        f"Sending crypto for reference ID: {transfer_details.reference_id}"
    )
    try:
        async with httpx.AsyncClient() as client:
             # Map TransferDetails to the expected CryptoSendRequest structure
            request_data = {
                "source_wallet_id": transfer_details.source_wallet_id,
                "dest_wallet_id": transfer_details.destination_wallet_id,
                "reference_id": transfer_details.reference_id,
                # Amount is not in the mock server request model, so we don't send it
            }
            response = await client.post(
                f"{MOCK_SERVER_URL}/send_crypto",
                json=request_data,
            )
            response.raise_for_status()
            result = response.json()
            transaction_id = result.get("transaction_id")
            status = result.get("status", "N/A")
            activity.logger.info(
                f"Crypto send status '{status}' with transaction ID '{transaction_id}' for reference ID: {transfer_details.reference_id}"
            )
            if status != "sent" or not transaction_id:
                 raise ApplicationError(f"Crypto send failed with status: {status}", non_retryable=True)
            return transaction_id # Return the transaction_id upon success
    except httpx.HTTPStatusError as e:
        activity.logger.error(
            f"HTTP error {e.response.status_code} during crypto send for reference ID {transfer_details.reference_id}: {e.response.text}"
        )
        
        raise ApplicationError(f"Crypto send failed: {e.response.text}", non_retryable=False) from e
    except httpx.RequestError as e:
        activity.logger.error(
            f"HTTP request failed during crypto send for reference ID {transfer_details.reference_id}: {e!r}"
        )
        raise ApplicationError(f"Crypto send failed: {e}", non_retryable=True) from e
    except Exception as e:
        activity.logger.error(
            f"An unexpected error occurred during crypto send for reference ID {transfer_details.reference_id}: {e!r}"
        )
        raise ApplicationError(
            f"Unexpected error during crypto send: {e}", non_retryable=True
        ) from e
