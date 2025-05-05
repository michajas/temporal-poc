from pydantic import BaseModel


CRYPTO_TRANSFER_TASK_QUEUE_NAME = "CRYPTO_TRANSFER_TASK_QUEUE"


class TransferDetails(BaseModel):
    source_wallet_id: str
    destination_wallet_id: str
    card_number: str
    amount: float
    reference_id: str

