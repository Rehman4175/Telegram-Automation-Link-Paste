import os
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, RPCError
import asyncio

# Load environment variables from config.env
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']
phone_number = os.environ['PHONE_NUMBER']
group = os.environ['GROUP']
messages = [os.environ[f'MESSAGE_{i+1}'] for i in range(5)]

# Create the client and connect using phone number
client = TelegramClient('session_name', api_id, api_hash)

# Dictionary to keep track of wait times for each group
group_wait_times = {}

async def send_messages():
    await client.start(phone_number)

    while True:
        try:
            # Skip group if it's in wait time
            if group in group_wait_times and group_wait_times[group] > 0:
                print(f'Waiting for {group_wait_times[group]} seconds before retrying {group}')
                group_wait_times[group] -= 10  # Reduce wait time by 10 seconds
                continue

            message = messages[0]  # Send the first message
            group_entity = await client.get_entity(group)
            await client.send_message(group_entity, message)
            print(f'Message sent to {group}: {message}')

            # Cycle through messages
            messages.append(messages.pop(0))

        except FloodWaitError as e:
            print(f'Rate limit hit for {group}, waiting for {e.seconds} seconds.')
            group_wait_times[group] = e.seconds
            continue  # Skip to the next iteration

        except RPCError as e:
            print(f'RPC error for {group}: {e}. Skipping this group/message.')
            continue  # Skip to the next iteration

        except Exception as e:
            print(f'Error sending message to {group}: {e}')
            continue  # Skip to the next iteration

        await asyncio.sleep(10)  # Wait for 10 seconds before sending the next message

with client:
    client.loop.run_until_complete(send_messages())