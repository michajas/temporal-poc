import asyncio
import traceback

from temporalio.client import Client, WorkflowFailureError

from temporal_poc.shared import CRYPTO_TRANSFER_TASK_QUEUE_NAME, AuthorizeInput, TransferDetails
from temporal_poc.workflow import CryptoTransfer


async def main() -> None:
    # Create client connected to server at the given address
    client: Client = await Client.connect("localhost:7233")

    data: TransferDetails = TransferDetails(
        source_wallet_id="0x11001",
        destination_wallet_id="0x00100",
        card_number="1234567890123456",
        amount=250,
        reference_id="12345",
    )

    try:
        result = await client.start_workflow(
            CryptoTransfer.run,
            data,
            id="crypto-transfer-v1",
            task_queue=CRYPTO_TRANSFER_TASK_QUEUE_NAME,
        )
        print(f"Started workflow. Workflow ID: {result.id}")
        print(f"Waiting for incoming simulated webhook")

        # Simulate webhook
        await asyncio.sleep(5)
        signal_result = await result.signal(
            CryptoTransfer.approve,
            AuthorizeInput(name="Card XXX"),
        )
        print(await result.result())

    except WorkflowFailureError:
        print("Got expected exception: ", traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
