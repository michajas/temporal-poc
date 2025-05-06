from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

from temporal_poc.shared import AuthorizeInput


# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from temporal_poc.activities import authorize_payment, verify_wallet, send_crypto
    from temporal_poc.shared import TransferDetails

@workflow.defn
class CryptoTransfer:
    def __init__(self):
        self.payment_authorized = False
        

    @workflow.run
    async def run(self, transfer_details: TransferDetails) -> str:
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            maximum_interval=timedelta(seconds=2),
            # non_retryable_error_types=["InvalidAccountError", "InsufficientFundsError"],
        )
        
        verify_wallet_result = await workflow.execute_activity(
            verify_wallet, 
            transfer_details, 
            start_to_close_timeout=timedelta(seconds=5), 
            retry_policy=retry_policy
        )

        authorize_payment_result = await workflow.execute_activity(
            authorize_payment, 
            transfer_details, 
            start_to_close_timeout=timedelta(seconds=5), 
            retry_policy=retry_policy
        )
        
        workflow.logger.info("Waiting for authorization")
        await workflow.wait_condition(
            lambda: self.payment_authorized
        )
        workflow.logger.info("Authorized payment")
        
        send_crypto_result = await workflow.execute_activity(
            send_crypto, 
            transfer_details, 
            start_to_close_timeout=timedelta(seconds=5), 
            retry_policy=retry_policy
        )
        
        return f"Authorized payment: {authorize_payment_result}, Verified wallet: {verify_wallet_result}, Sent crypto: {send_crypto_result}"

    @workflow.signal
    def approve(self, input: AuthorizeInput) -> None:
        # 👉 A Signal handler mutates the Workflow state but cannot return a value.
        self.payment_authorized = True
