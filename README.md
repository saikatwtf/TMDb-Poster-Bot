# TMDb-Poster-Bot

A Telegram bot that allows users to search for movies or TV shows using the TMDb API and returns posters, backdrops, and details in an interactive format.

## Developer

Developed by [Saikat](https://github.com/saikatwtf)

## Features

- Search for movies and TV shows using TMDb API
- Display posters and backdrops with high-resolution options
- Multilingual metadata support
- Interactive button-based navigation

## Configuration

### Getting API Keys

#### TMDb API Key
1. Create an account on [The Movie Database](https://www.themoviedb.org/)
2. Go to your [account settings](https://www.themoviedb.org/settings/api)
3. Click on "API" in the left sidebar
4. Follow the steps to request an API key for a "Developer" application
5. Once approved, you'll receive an API key (v3 auth)

#### Telegram Bot Token
1. Start a chat with [@BotFather](https://t.me/BotFather) on Telegram
2. Send the command `/newbot` and follow the instructions
3. Once created, you'll receive a token for your bot

### Configuration File
The `config.py` file contains important settings for the bot:

- **API Keys**: Loaded from environment variables
- **TMDb URLs**: Base URLs for the TMDb API and image server
- **Image Sizes**: Different resolution options for posters and backdrops
- **Supported Languages**: Currently supports English, Hindi, Tamil, Telugu, and Bengali

You can modify this file to add more languages or change image size preferences.

## Setup

### Local Setup
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys (see `.env.example`)
4. Run the bot: `python bot.py`

### Deploy to Heroku
Click the button below to deploy to Heroku:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

## Commands

- `/start` - Welcome message and instructions
- `/tmdb <movie or show name>` - Search for movies or TV shows
- `/trndb <movie or show name>` - Alternative search command (works the same as `/tmdb`)

## License

This project is maintained by [Saikat](https://github.com/saikatwtf). See the LICENSE file for details.