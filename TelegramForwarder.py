import time
import asyncio
from telethon.sync import TelegramClient
from telethon import errors
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)

    async def forward_all_messages_to_channel(self, source_chat_id, destination_channel_id):
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            try:
                await self.client.sign_in(self.phone_number, input('Enter the code: '))
            except errors.rpcerrorlist.SessionPasswordNeededError:
                password = input('Two-step verification is enabled. Enter your password: ')
                await self.client.sign_in(password=password)

        print(f"Fetching messages from source chat {source_chat_id}...")

        # Fetch all messages from the source chat
        messages = await self.client.get_messages(source_chat_id, limit=None)
        print(f"Total messages fetched: {len(messages)}")

        # Forward each message to the destination channel
        for message in reversed(messages):  # Forward from oldest to newest
            try:
                if message.media:  # Handle media messages
                    print(f"Forwarding media message ID: {message.id}")
                    # Forward the entire message with media
                    await message.forward_to(destination_channel_id)
                elif message.text:  # Handle text messages
                    print(f"Forwarding text message ID: {message.id}")
                    await self.client.send_message(destination_channel_id, message.text)
                else:
                    print(f"Skipping unsupported message type: {message}")
                    continue

                print(f"Successfully forwarded message ID: {message.id}")
            except Exception as e:
                print(f"Failed to forward message ID {message.id}: {e}")
            
            # Add a small delay to prevent rate limiting
            await asyncio.sleep(2)  # Increased delay to be safer with media files

        print("All messages forwarded successfully!")

    async def list_chats(self):
        """List all chats and their IDs"""
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            try:
                await self.client.sign_in(self.phone_number, input('Enter the code: '))
            except errors.rpcerrorlist.SessionPasswordNeededError:
                password = input('Two-step verification is enabled. Enter your password: ')
                await self.client.sign_in(password=password)

        async for dialog in self.client.iter_dialogs():
            print(f"Chat ID: {dialog.id} - Name: {dialog.name}")

# Function to read credentials from file
def read_credentials():
    try:
        with open("credentials.txt", "r") as file:
            lines = file.readlines()
            api_id = lines[0].strip()
            api_hash = lines[1].strip()
            phone_number = lines[2].strip()
            return api_id, api_hash, phone_number
    except FileNotFoundError:
        print("Credentials file not found.")
        return None, None, None

# Function to write credentials to file
def write_credentials(api_id, api_hash, phone_number):
    with open("credentials.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")

async def main():
    # Attempt to read credentials from file
    api_id, api_hash, phone_number = read_credentials()

    # If credentials not found in file, prompt the user to input them
    if api_id is None or api_hash is None or phone_number is None:
        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        phone_number = input("Enter your phone number: ")
        # Write credentials to file for future use
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    
    print("Choose an option:")
    print("1. List Chats")
    print("2. Forward All Messages")
    
    choice = input("Enter your choice: ")
    
    if choice == "1":
        await forwarder.list_chats()
    elif choice == "2":
        source_chat_id = int(input("Enter the source chat ID: "))
        destination_channel_id = int(input("Enter the destination chat ID: "))
        await forwarder.forward_all_messages_to_channel(source_chat_id, destination_channel_id)
    else:
        print("Invalid choice")

# Start the event loop and run the main function
if __name__ == "__main__":
    asyncio.run(main())
