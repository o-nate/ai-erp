# AI ERP WhatsApp Bot Prototype

This project is a prototype of an agentic AI-based Enterprise Resource Planning (ERP) system. The goal is to provide an easy-to-use interface for interacting with the ERP functionalities through a simple WhatsApp messaging interface.

**Please Note:** This is a _prototype_ and not intended for production use.

[![AI ERP WhatsApp Bot Demo](https://img.youtube.com/vi/2yOuya2JqsU/0.jpg)](https://www.youtube.com/watch?v=2yOuya2JqsU)

## Features

- Interact with ERP functions via WhatsApp messages.
- Utilizes agentic AI principles to process requests.
- Simple setup for local development using ngrok.

## Prerequisites

Before getting started, you will need accounts and credentials from the following services:

1.  **Meta for Developers:** To use the WhatsApp Business API, you need a Meta for Developers account, set up a Business Account, and create a WhatsApp Business App. You will need the App ID, a Test Phone Number, a Phone Number ID, a Temporary Access Token (for testing), and set up a Webhook with a Verify Token.
    a. Create your Meta developer account [here](https://developers.facebook.com/docs/development/register).

    b. Visit your developer dashboard and create a new app.

    c. Add your Meta Business Account, or create one if/when prompted.

    d. Add WhatsApp to your app.

    e. In the app dashboard, navigate to `WhatsApp > API Setup` and follow the steps to 'Send and receive messages.' This will provide you with a test phone number. You must also include phone numbers that will have access to send your test account messages.

    f. Generate an access token. Add this as `WHATSAPP_API_KEY` in your `.env` file.

2.  **LangSmith:** This project uses LangSmith for tracing and debugging the AI agent's execution. You will need a LangSmith account and an API key. Visit the [LangSmith website](https://www.langchain.com/langsmith) for details.

3.  **ngrok:** To receive messages from the WhatsApp Business API webhook during local development, you will need to expose your local server to the internet using ngrok. You can download and set up ngrok from their [official website](https://ngrok.com/download).

## Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/o-nate/ai-erp.git
    cd ai-erp
    ```
2.  **Set up a Python virtual environment** (recommended):

    Create the `venv`:

    ```bash
    py -3.10 -m venv venv
    ```

    Activate the `venv`:

    ```bash
    # On Windows
    .\venv\Scripts\activate
    # On macOS and Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration (.env file)

Create a file named `.env` in the root directory of the project. This file will store your sensitive credentials and configuration settings. You can use the provided `.env.example` as a template.

Fill in the following variables with your actual credentials:

- `ENV`: Define if this is a test/dev or production environment.
- `WHATSAPP_PHONE_NUMBER_ID`: The ID of the WhatsApp test phone number provided by Meta.
- `WHATSAPP_API_KEY`: Your temporary or permanent Meta Access Token.
- `VERIFICATION_TOKEN`: The Verify Token you set up in the Meta Webhook configuration.
- `LANGSMITH_TRACING`: Set to `true` to enable LangSmith tracing.
- `LANGSMITH_ENDPOINT`: API URL.
- `LANGSMITH_API_KEY`: Your LangSmith API key.
- `LANGSMITH_PROJECT`: (Optional) A name for your project in LangSmith.
- `OPENAI_API_KEY`: Your OpenAI API key.
- `ALLOWED_USERS_LIST`: A semicolon-separated list of allowed users, where each user's details are comma-separated (id, phone, first_name, last_name, role).

## Running Locally

1.  **Start ngrok:**

    Open your terminal in a new session (or keep the virtual environment active if you prefer) and run ngrok to expose your local server port (assuming the app runs on port 8000):

    ```bash
    ngrok http 8000
    ```

    Ngrok will provide you with a public URL (e.g., `https://your-random-subdomain.ngrok.io`). Keep this terminal window open.

2.  **Configure Meta Webhook:**

    In your Meta for Developers dashboard for your WhatsApp Business App, configure the Webhook URL using the public ngrok URL with the `/webhook` endpoint appended (e.g., `https://your-random-subdomain.ngrok.io/webhook`). Use the `META_VERIFY_TOKEN` you defined in your `.env` file.

    a. Return to your app on [Meta for Developers](https://developers.facebook.com/apps/).

    b. Go to `WhatsApp > Configuration > Webhook` and under 'Select product', choose WhatsApp Business Account.

    c. Copy-paste the public URL from ngrok (e.g., `https://your-random-subdomain.ngrok.io`) in the 'Callback URL' field and the `VERIFICATION_TOKEN` value from your `.env` file in the 'Verfiy token' field. <b>Note: You must define this `VERIFICATION_TOKEN`.</b>

    d. Click the 'Verify and save' button, and wait for verifcation to complete.

    e. Locate the 'messages' Field under 'Webhook fields,' and turn 'Subscribed' on.

3.  **Run the application:**

    In your project terminal session (where your virtual environment is active), run the main application file from the root directory using:

    ```bash
    python -m app.main
    ```

    Alternatively, you navigate the the `app/` directory in the project terminal session and run:

    ```bash
    uvicorn main:app --reload
    ```

    Keep this terminal window open.

Your application should now be running locally and accessible via the ngrok URL, ready to receive messages from your Meta test phone number.

Simply ensure you have add any phone numbers associated with the `ALLOWED_USERS_LIST` to the list of recipient phone numbers on the Meta platform in API Setup.

<b>Note: If you would like to begin testing with mock data, run the `mock_data` module from your root directory:</b>

```bash
python -m app.persistance.mock_data
```
