import asyncio

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from temporal_poc.activities import authorize_payment, verify_wallet, send_crypto
from temporal_poc.workflow import CryptoTransfer
from temporal_poc.shared import CRYPTO_TRANSFER_TASK_QUEUE_NAME



async def main():
    client = await Client.connect("localhost:7233", namespace="default")
    # Run the worker
    worker = Worker(
        client, 
        task_queue=CRYPTO_TRANSFER_TASK_QUEUE_NAME, 
        workflows=[CryptoTransfer], 
        activities=[authorize_payment, verify_wallet, send_crypto]
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
