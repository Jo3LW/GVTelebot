# Golden Village Ticket Telegram Bot with Docker-Selenium-Lambda

This project demonstrates the use of headless Chrome and Selenium on a container image deployed to AWS Lambda. The main purpose is to create a Telegram bot that provides information about movie showtimes and cinemas using the Golden Village ticketing platform.

The Docker-Selenium-Lambda image in this project is configured with the following versions:
- Python 3.11.4
- Chromium 114.0.5735.0
- Chromedriver 114.0.5735.90
- Selenium 4.9.1

## Prerequisites

Before deploying and using GVTelebot, make sure you have the following:

- [Serverless Framework](https://www.serverless.com/framework/docs/getting-started/)
- [AWS Account](https://aws.amazon.com/)
- [Telegram Bot API Token](https://core.telegram.org/bots#botfather)

## Running the bot

```bash
$ npm install -g serverless # skip this line if you have already installed Serverless Framework
$ export AWS_REGION=ap-northeast-1 # You can specify region or skip this line. us-east-1 will be used by default.
$ sls create --template-url "https://github.com/Jo3LW/GVTelebot/tree/main" --path dGVTeleBot && cd $_
$ sls deploy
$ sls invoke --function bot
```

## Configuration
Before deploying and using this bot, you need to set up your own Telegram Bot API token. Follow these steps:

1. Create a new bot on Telegram by talking to the [BotFather](https://core.telegram.org/bots#botfather).
2. Copy the generated API token.
3. Open the `main.py` file in the `GVTeleBot` directory.
4. Find the following lines:

   ```python
   # Set your Telegram Bot API token here
   BOT_TOKEN = 'YOUR_BOT_TOKEN'
   bot = telebot.TeleBot(BOT_TOKEN)
   ```
5. Replace 'YOUR_BOT_TOKEN' with your actual API token.
## Usage

1. Start a chat with your Telegram bot by searching for its username.
2. Use the following commands to interact with the bot:

   - `/start`: Begin the conversation and see the list of available movies as buttons.
   - Click on a movie button to see the available cinemas for that movie.
   - Click on a cinema button to see the movie timings for different days.
   - Click on a day\'s timing to view the showtimes for that movie at the selected cinema on that day.

## Customization

You can customize and extend the functionality of GVTelebot by modifying the `main.py` file in the `GVTeleBOt` directory. This is where you can define additional commands, responses, and interactions with users.

## Credits

This project is based on the `docker-selenium-lambda` template by umihico, which enables running headless Chrome and Selenium on AWS Lambda.

## Screenshots

<br>
<em>The start command displays a list of movies as buttons.</em>
<img src="https://gvbotimages.s3.ap-southeast-1.amazonaws.com/start.PNG" alt="Screenshot of start command" width="400"/>

<br>
<em>Clicking on a movie displays the list of available cinemas as buttons.
</em>
<img src="https://gvbotimages.s3.ap-southeast-1.amazonaws.com/movies.PNG" alt="Screenshot of start command" width="400"/>

<br>
<em>Clicking on a cinema button displays the list of available timings for different days.
</em>
<img src="https://gvbotimages.s3.ap-southeast-1.amazonaws.com/cinemas.PNG" alt="Screenshot of start command" width="400"/>


