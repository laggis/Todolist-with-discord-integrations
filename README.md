# Discord TODO List

A web-based TODO list application that integrates with Discord to keep your server members updated about your tasks.

## Features

- Create, update, and delete TODOs
- Mark tasks as completed/pending
- Automatic Discord notifications for all actions
- Clean and responsive web interface
- Real-time updates to your Discord server

## Setup Instructions

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up Discord Webhook:
   - In your Discord server, go to Server Settings > Integrations > Webhooks
   - Create a new webhook and copy the webhook URL
   - Copy `.env.example` to `.env`
   - Replace `your_discord_webhook_url_here` with your actual webhook URL

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and go to `http://localhost:5000`

## Usage

- Add new TODOs using the form at the top of the page
- Mark TODOs as complete/pending using the buttons
- Delete TODOs when they're no longer needed
- All actions will automatically send notifications to your Discord server

## Note

Make sure to keep your webhook URL private and never share it publicly.
