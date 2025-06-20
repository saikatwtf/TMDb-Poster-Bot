# Deployment Guide

This guide explains how to deploy the TMDb Poster Bot to different platforms.

## Prerequisites

1. A Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))
2. A TMDb API Key (get it from [TMDb Developer](https://www.themoviedb.org/settings/api))

## Local Deployment

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys (use `.env.example` as a template)
4. Run the bot:
   ```
   python bot.py
   ```

## Heroku Deployment

### Option 1: One-Click Deployment

1. Click the "Deploy to Heroku" button in the README
2. Fill in your Telegram Bot Token and TMDb API Key
3. Click "Deploy App"
4. Once deployed, ensure the worker dyno is running in the Heroku dashboard

### Option 2: Manual Deployment

1. Create a Heroku account if you don't have one
2. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Login to Heroku:
   ```
   heroku login
   ```
4. Create a new Heroku app:
   ```
   heroku create your-app-name
   ```
5. Add a `Procfile` to your repository with the following content:
   ```
   worker: python bot.py
   ```
6. Set environment variables:
   ```
   heroku config:set TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   heroku config:set TMDB_API_KEY=your_tmdb_api_key
   ```
7. Deploy to Heroku:
   ```
   git push heroku main
   ```
8. Start the worker dyno:
   ```
   heroku ps:scale worker=1
   ```

## VPS Deployment

1. SSH into your VPS
2. Install Python and required packages:
   ```
   sudo apt update
   sudo apt install python3 python3-pip git
   ```
3. Clone the repository:
   ```
   git clone https://github.com/saikatwtf/TMDb-Poster-Bot.git
   cd TMDb-Poster-Bot
   ```
4. Install dependencies:
   ```
   pip3 install -r requirements.txt
   ```
5. Create a `.env` file with your API keys
6. Set up a systemd service for persistent running:
   
   Create a file `/etc/systemd/system/tmdb-bot.service`:
   ```
   [Unit]
   Description=TMDb Poster Telegram Bot
   After=network.target

   [Service]
   User=your_username
   WorkingDirectory=/path/to/TMDb-Poster-Bot
   ExecStart=/usr/bin/python3 /path/to/TMDb-Poster-Bot/bot.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
7. Enable and start the service:
   ```
   sudo systemctl enable tmdb-bot
   sudo systemctl start tmdb-bot
   ```
8. Check status:
   ```
   sudo systemctl status tmdb-bot
   ```

## Notes

- TMDb API has a rate limit of 40 requests per 10 seconds
- For production use, consider implementing caching to reduce API calls
- Monitor your bot's performance and adjust resources as needed