# Telegram Bot to AWS S3 with API Gateway and Lambda

This project demonstrates how to integrate a **Telegram Bot** with **AWS S3** using **AWS Lambda** and **API Gateway**. The bot allows users to upload files (restricted to PDFs, DOC, DOCX, and TXT) to an S3 bucket, and sends a confirmation message to a Telegram group once the file is uploaded successfully.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture](#architecture)
- [AWS Setup](#aws-setup)
  - [Create an S3 Bucket](#create-an-s3-bucket)
  - [Create Lambda Function](#create-lambda-function)
  - [Set Up API Gateway](#set-up-api-gateway)
  - [Configure API Gateway Mapping Template](#configure-api-gateway-mapping-template)
- [Telegram Webhook Setup](#telegram-webhook-setup)
- [Telegram bot Setup](#Telegram-Bot-Setup)

## Prerequisites

Before starting, ensure you have the following:

- **AWS Account** (with S3, Lambda, and API Gateway access)
- **Telegram Bot** (created using [BotFather](https://core.telegram.org/bots#botfather))
- **AWS CLI** and **SAM CLI** (optional but recommended for testing and deployment)

## Architecture

- **Telegram Bot**: Receives user uploads via the Telegram app.
- **API Gateway**: Acts as the entry point for the Telegram webhook.
- **Lambda Function**: Processes the webhook, uploads the file to S3, and sends a confirmation message back to the user.
- **S3**: Stores the uploaded files securely.

## AWS Setup

### 1. Create an S3 Bucket

1. Navigate to **S3** in the AWS Management Console.
2. Click **Create bucket**.
3. Set a bucket name (e.g., `telegram-bot-s3-uploads`).
4. Select the desired AWS region.
5. Leave other settings as default and click **Create bucket**.

### 2. Create Lambda Function

1. Go to **Lambda** in the AWS Console.
2. Click **Create function**.
3. Select **Author from scratch** and name the function (e.g., `telegram-bot-s3-handler`).
4. Set the runtime to **Python 3.x**.
5. Assign a role with **S3 Full Access** or create a new role if needed.

#### Environment Variables

Add the following environment variables to your Lambda function:

- `TELEGRAM_BOT_TOKEN`: The token for your Telegram bot.
- `S3_BUCKET_NAME`: The name of your S3 bucket.

#### Lambda Python Code

Create a Lambda function that does the following:

1. Validates that the incoming webhook data contains a file.
2. Downloads the file from Telegram using the file ID.
3. Restricts uploads to specific document types (PDF, DOC, DOCX, TXT).
4. Uploads the file to the S3 bucket.
5. Sends a confirmation message back to the Telegram group once the file is successfully uploaded.

Make sure to handle cases where the uploaded file type is not allowed by sending an appropriate message back to the Telegram group.

### 3. Set Up API Gateway

1. Navigate to **API Gateway** and create a new **HTTP API**.
2. Create a **POST** method for the `/webhook` resource.
3. Set up **Lambda Integration** to point to your Lambda function.
4. Deploy the API.

### 4. Configure API Gateway Mapping Template

1. Go to the **Integration Request** for the POST `/webhook` method.
2. Add a **Body Mapping Template** for `application/json`:

   ```json
   {
     "body": $input.json('$'),
     "headers": {
       #foreach($header in $input.params().header.keySet())
         "$header": "$input.params().header.get($header)"#if($foreach.hasNext),#end
       #end
     }
   }
3. Save and Deploy the API.

### 5. telegram-webhook-setup

Use the following curl command to set up the Telegram webhook:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<YOUR_API_GATEWAY_URL>/webhook"
```
Replace <YOUR_BOT_TOKEN> with your Telegram bot token and <YOUR_API_GATEWAY_URL> with the API Gateway URL.

## Telegram Bot Setup

To interact with Telegram and upload files to AWS S3, you need to set up a Telegram bot using **BotFather** and configure it to use the webhook provided by your API Gateway.

### Step 1: Create a Telegram Bot Using BotFather

1. **Open Telegram** on your mobile or desktop app.
2. **Search for** `BotFather` in the search bar and start a chat with it.
3. **Start the Bot Setup**:
   - Type `/start` and press enter to get a list of available commands.
4. **Create a New Bot**:
   - Type `/newbot` and press enter.
   - BotFather will ask for a **name** for your bot (e.g., `FileUploadBot`).
   - After providing the name, it will ask for a **username** for the bot. The username must end with `bot` (e.g., `fileupload_bot`).
5. **Receive the Bot Token**:
   - After setup, BotFather will give you a **token** that looks like this:
     ```
     123456789:ABCdefGhIjklMNOpqRstuvWXYZ0123456789
     ```
   - **Save this token**; it will be required for API requests.
  
6. **Disable Privacy Mode for the Bot**
To allow the bot to see all messages and files in the group (including those not directed at it), you need to disable privacy mode.

Open BotFather in Telegram.
Type `/mybots` and select your bot.
Go to Bot Settings.
Choose Group Privacy and set it to Disabled. This will allow your bot to monitor all messages in the group, not just commands.


### Step 2: Set Up a Telegram Group (Optional)

If you want the bot to work in a Telegram group, you can follow these steps to create a group and add the bot:

1. **Create a New Group**:
   - In Telegram, tap the **menu** icon (or **new message** icon) and select **New Group**.
2. **Add Members**:
   - Add the participants and the **bot** (by searching for its username, e.g., `fileupload_bot`).
3. **Give Admin Rights to the Bot** (Optional):
   - If needed, you can give the bot admin rights by going to the group settings and selecting **Administrators**.

### Step 3: Configure the Webhook for Your Telegram Bot

To handle incoming messages or files, you need to set a webhook that points to your API Gateway URL.

1. **Set the Webhook**:
   - Run the following `curl` command to set up the webhook:

     ```bash
     curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<YOUR_API_GATEWAY_URL>/webhook"
     ```

   - Replace `<YOUR_BOT_TOKEN>` with the token you received from BotFather.
   - Replace `<YOUR_API_GATEWAY_URL>` with your API Gateway's public URL (e.g., `https://abcd1234.execute-api.region.amazonaws.com/webhook`).

2. **Verify the Webhook**:
   - Use the following command to check if the webhook is set up correctly:

     ```bash
     curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
     ```

   - You should see a response similar to:
     ```json
     {
       "ok": true,
       "result": {
         "url": "https://your-api-gateway-url/webhook",
         "has_custom_certificate": false,
         "pending_update_count": 0
       }
     }
     ```

3. **Delete the Webhook** (Optional):
   - If you need to remove the webhook, you can use this command:

     ```bash
     curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"
     ```

### Step 4: Test the Telegram Bot

1. **Send a File**:
   - Send a document (e.g., PDF, DOC, DOCX, TXT) to your bot (or in the group where your bot is added).
2. **Monitor Lambda Logs**:
   - Your Lambda function should process the message and upload the file to S3.
3. **Receive a Confirmation**:
   - Once the file is uploaded to S3, the bot will send a confirmation message back to the chat.

### Step 5: Add More Features (Optional)

- **Error Handling**:
  - You can modify the Lambda function to handle errors and send appropriate messages back to users.
  
- **Adding Custom Commands**:
  - You can add custom commands to your bot using BotFather (e.g., `/upload`, `/help`).

To add commands:
1. Go back to **BotFather**.
2. Type `/setcommands` and follow the instructions to add custom commands.
---
# Steps to Add External Libraries (like `requests`) to Lambda

## 1. Set Up a Local Development Environment
First, ensure you have a local development environment with the necessary dependencies installed (e.g., Python 3.x).

## 2. Create a Local Directory for Your Lambda Function
Create a directory where you will store your Lambda function and its dependencies:

```bash
    mkdir lambda_function
    cd lambda_function
```

## 3. Install the `requests` Library Locally
Install the `requests` module and any other required modules in this directory using pip:

```bash
    pip install requests -t .
```

    This command will download the `requests` library (and its dependencies) and place them in the current directory (`lambda_function`), so you can package them with your Lambda function.

## 4. Add Your Lambda Function Code
Create or copy your Lambda function (e.g., `lambda_function.py`) in this directory. Here’s an example of the file structure:

    ```
    lambda_function/
    ├── requests/           # The installed requests library
    ├── urllib3/            # Requests' dependency
    ├── certifi/            # Requests' dependency
    ├── chardet/            # Requests' dependency
    ├── lambda_function.py  # Your Lambda function code
    ```

## 5. Zip the Function and Dependencies
Once you've installed the dependencies and added your Lambda function code, zip the contents of the directory to upload it to Lambda:

### For Linux/Mac:

```bash
    zip -r lambda_function.zip .
```

### For Windows (in Command Prompt or PowerShell):

```bash
    Compress-Archive -Path * -DestinationPath lambda_function.zip
```

## 6. Upload the ZIP File to AWS Lambda
1. Go to the [AWS Lambda Console](https://console.aws.amazon.com/lambda/).
2. Select the Lambda function where you encountered the error.
3. In the **Code** section, choose **Upload from** > **.zip file**.
4. Upload the `lambda_function.zip` file you just created.

## 7. S3 Policy for Lambda
``` json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::your-s3-bucket-name/*"
    }
  ]
}
```   

## 8. Test the Lambda Function
After the upload is complete, test your Lambda function by sending a document through your Telegram bot. It should now execute successfully without the "No module named 'requests'" error.
