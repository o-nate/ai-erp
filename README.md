# AI ERP Prototype

This project is a prototype of an agentic AI-based Enterprise Resource Planning (ERP) system. The goal is to provide an easy-to-use interface for interacting with the ERP functionalities through a simple WhatsApp messaging interface.

**Please Note:** This is a *prototype* and not intended for production use.

## Features

*   Interact with ERP functions via WhatsApp messages.
*   Utilizes agentic AI principles to process requests.
*   Simple setup for local development using ngrok.

## Prerequisites

Before getting started, you will need accounts and credentials from the following services:

1.  **Meta for Developers:** To use the WhatsApp Business API, you need a Meta for Developers account, set up a Business Account, and create a WhatsApp Business App. You will need the App ID, a Test Phone Number, a Phone Number ID, a Temporary Access Token (for testing), and set up a Webhook with a Verify Token. You can find more information [here](https://developers.facebook.com/docs/whatsapp/guides/get-started).
2.  **LangSmith:** This project uses LangSmith for tracing and debugging the AI agent's execution. You will need a LangSmith account and an API key. Visit the [LangSmith website](https://www.langchain.com/langsmith) for details.
3.  **ngrok:** To receive messages from the WhatsApp Business API webhook during local development, you will need to expose your local server to the internet using ngrok. You can download and set up ngrok from their [official website](https://ngrok.com/download).

## Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/o-nate/ai-erp.git
    cd ai-erp
    ```
2.  **Set up a Python virtual environment** (recommended):

    ```bash
    python -m venv venv
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

*   `ENV`: Define if this is a test/dev or production environment.
*   `WHATSAPP_PHONE_NUMBER_ID`: The ID of the WhatsApp test phone number provided by Meta.
*   `WHATSAPP_API_KEY`: Your temporary or permanent Meta Access Token.
*   `VERIFICATION_TOKEN`: The Verify Token you set up in the Meta Webhook configuration.
*   `LANGSMITH_TRACING`: Set to `true` to enable LangSmith tracing.
*   `LANGSMITH_ENDPOINT`: API URL.
*   `LANGSMITH_API_KEY`: Your LangSmith API key.
*   `LANGSMITH_PROJECT`: (Optional) A name for your project in LangSmith.
*   `OPENAI_API_KEY`: Your OpenAI API key.
*   `ALLOWED_USERS_LIST`: A semicolon-separated list of allowed users, where each user's details are comma-separated (id, phone, first_name, last_name, role).

## Running Locally

1.  **Start ngrok:**

    Open your terminal in a new session (or keep the virtual environment active if you prefer) and run ngrok to expose your local server port (assuming the app runs on port 8000):

    ```bash
    ngrok http 8000
    ```

    Ngrok will provide you with a public URL (e.g., `https://your-random-subdomain.ngrok.io`). Keep this terminal window open.

2.  **Configure Meta Webhook:**

    In your Meta for Developers dashboard for your WhatsApp Business App, configure the Webhook URL using the public ngrok URL with the `/webhook` endpoint appended (e.g., `https://your-random-subdomain.ngrok.io/webhook`). Use the `META_VERIFY_TOKEN` you defined in your `.env` file.

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

Simply ensure you have add

## Contributing

(Optional section: Add instructions here if you welcome contributions)

## License

(Optional section: Add license information here)
