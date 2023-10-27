# telegram_suggest_bot
This Python script utilizes the Telebot library to create a Telegram bot capable of handling post suggestions and user feedback. The bot is designed to help users suggest posts for a channel and communicate with the administrators for feedback purposes. Below are the key functionalities and components of this code:

## Features

Post Suggestions:
- Users can initiate the post suggestion process by clicking the "Suggest Post" button.
- Users send a post to the bot, which is then forwarded to administrators for approval.
- Administrators can choose to post the suggested content to the channel.

User Feedback:
- Users can provide feedback by clicking the "Feedback" button.
- Feedback messages are forwarded to administrators.
- Administrators can reply to the feedback, and the replies are sent back to the respective users.


## Build & running

1. Clone the repo

2. Build the Docker image
``` 
docker build -t suggest_bot .
```

3. Run the Docker container
``` 
docker run -d --name=suggest_bot --restart=unless-stopped suggest_bot

```

4. ????

5. PROFIT!!!11