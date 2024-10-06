import json
import boto3
import requests
import os

# Initialize AWS S3 client
s3 = boto3.client('s3')

# Retrieve environment variables
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

# Function to send a message back to the Telegram user
def send_telegram_message(chat_id, text):
    send_message_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(send_message_url, json=payload)
    
    # Log the response from Telegram
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")
    else:
        print(f"Message sent successfully: {response.json()}")

def lambda_handler(event, context):
    try:
        # Ensure body is present
        if 'body' not in event:
            raise Exception("No body in event")
        
        # If the body is a string, parse it as JSON
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        
        print(f"Webhook received: {body}")

        # Get the chat ID from the message
        chat_id = body['message']['chat']['id']
        
        # Check if it's a document
        if 'document' in body['message']:
            file_id = body['message']['document']['file_id']
            file_name = body['message']['document']['file_name']

        # Check if it's a photo (Telegram sends photos in multiple sizes, we will get the largest one)
        elif 'photo' in body['message']:
            file_id = body['message']['photo'][-1]['file_id']  # Get the largest photo
            file_name = f"photo_{file_id}.jpg"  # Create a file name for the photo

        else:
            # If neither document nor photo, return an error
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "No document or photo received"})
            }

        # Step 1: Get the file path from Telegram
        get_file_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
        file_info = requests.get(get_file_url).json()
        file_path = file_info['result']['file_path']

        # Step 2: Download the file from Telegram
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        file_content = requests.get(file_url).content

        # Step 3: Upload the file to AWS S3
        s3.put_object(Bucket=S3_BUCKET_NAME, Key=file_name, Body=file_content)

        # Step 4: Send a confirmation message back to the Telegram group
        send_telegram_message(chat_id, f"File '{file_name}' uploaded to S3 successfully!")

        return {
            'statusCode': 200,
            'body': json.dumps({"status": "File uploaded successfully"})
        }

    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": f"Error processing webhook: {str(e)}"})
        }
