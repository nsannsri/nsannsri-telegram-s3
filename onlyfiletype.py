import json
import boto3
import requests
import os

# Initialize AWS S3 client
s3 = boto3.client('s3')

# Allowed file types
ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'txt']

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

            # Step 1: Check the file extension
            file_extension = file_name.split('.')[-1].lower()  # Get the file extension and convert it to lowercase
            if file_extension not in ALLOWED_EXTENSIONS:
                # Send a message back if the file type is not allowed
                send_telegram_message(chat_id, f"File type '{file_extension}' is not allowed. Please upload PDF, DOC, or TXT files.")
                return {
                    'statusCode': 400,
                    'body': json.dumps({"error": f"File type '{file_extension}' not allowed"})
                }

        else:
            # If it's not a document, return an error
            send_telegram_message(chat_id, "Only document uploads (PDF, DOC, or TXT) are allowed.")
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "No document received or unsupported file type"})
            }

        # Step 2: Get the file path from Telegram
        get_file_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
        file_info = requests.get(get_file_url).json()
        file_path = file_info['result']['file_path']

        # Step 3: Download the file from Telegram
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        file_content = requests.get(file_url).content

        # Step 4: Upload the file to AWS S3
        s3.put_object(Bucket=S3_BUCKET_NAME, Key=file_name, Body=file_content)

        # Step 5: Send a confirmation message back to the Telegram group
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
