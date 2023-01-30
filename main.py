import logging
import os
import chatGPT

from dotenv import load_dotenv

from telegramBot import TelegramBot

if __name__ == '__main__':
    load_dotenv()  # take environment variables from .env

    # Check if the .env variables are here
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    openai_api_token = os.getenv("OPENAI_API_TOKEN")
    user_allowed = os.getenv("USER_ALLOWED")

    if telegram_bot_token is None:
        print("add TELEGRAM_BOT_TOKEN to env")
        exit(1)
    if openai_api_token is None:
        print("add OPENAI_API_TOKEN to env")
        exit(1)
    if user_allowed is None:
        print("add USER_ALLOWED to env")
        exit(1)

    user_allowed = user_allowed.split(",")
    try:
        user_allowed = [int(i) for i in user_allowed]
    except ValueError:
        print('I need only INT in USER_ALLOWED')
        exit(1)

    ai = chatGPT.ChatGPT(openai_api_token)

    telegram_bot = TelegramBot(token=telegram_bot_token, ai=ai, allowed=user_allowed)
    telegram_bot.run()
