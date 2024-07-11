import asyncio
import os
import boto3
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import PeerChannel

# Load environment variables
telegram_session = os.getenv('TELEGRAM_SESSION')
api_id = int(os.getenv('TELEGRAM_API_ID'))
api_hash = os.getenv('TELEGRAM_API_HASH')
channel_id = int(os.getenv('TELEGRAM_CHANNEL_ID'))
target_channel_id = int(os.getenv('TELEGRAM_TARGET_CHANNEL_ID'))
s3_bucket = os.getenv('S3_BUCKET')
s3_key = os.getenv('S3_KEY')
search_text = os.getenv('SEARCH_TEXT')

# Initialize S3 client
s3_client = boto3.client('s3')

async def main():
    # Initialize TelegramClient using StringSession
    client = TelegramClient(StringSession(telegram_session), api_id, api_hash)

    try:
        # Connect to Telegram servers
        await client.start()

        # Get channel entities using channel_id and target_channel_id
        source_channel = await client.get_entity(PeerChannel(channel_id))
        target_channel = await client.get_entity(PeerChannel(target_channel_id))

        # Get last_message_id from S3
        last_message_id_obj = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        last_message_id = int(last_message_id_obj['Body'].read().decode('utf-8'))

        # Iterate over messages in source_channel starting from last_message_id
        async for message in client.iter_messages(source_channel, min_id=last_message_id, reverse=True):
            last_message_id = message.id
            # Check if the message contains the specified search text
            if search_text.lower() in message.message.lower():
                # Forward the message to the target channel
                await client.forward_messages(target_channel, message)

        # Update last_message_id in S3
        s3_client.put_object(Bucket=s3_bucket, Key=s3_key, Body=str(last_message_id))

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Disconnect from Telegram servers
        await client.disconnect()

# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())