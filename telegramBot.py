import asyncio
import redis
import pickle

from telegram.constants import ChatAction

from chatGPT import ChatGPT
from telegram import Update, Message, constants
from telegram.error import RetryAfter, BadRequest
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ChatMemberHandler, filters

r = redis.Redis(host='redis', port=6379, db=0)

class TelegramBot:
    def __init__(self, token: dict, ai: ChatGPT, allowed: [int]):
        self.bot_token = token
        self.ai = ai
        self.allowed = allowed

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles the /start
        """
        await update.message.reply_text("/start - Start the bot"
                                        "\n/gen - Create text"
                                        "\nMade by @SPUZ_FEED")

    def is_allowed(self, user: int) -> bool:
        """
        Check if user in allow list
        """
        return user in self.allowed

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /start
        """
        if not self.is_allowed(update.message.from_user.id):
            return

        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a @SPUZ_FEED")

    async def prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /start
        """
        message_text = ''

        if not self.is_allowed(update.message.from_user.id):
            return

        if update.message.entities:
            if update.message.entities[0]:
                if update.message.entities[0].type=="mention":
                    if update.message.text.split(' ',1)[0]=='@neiropiki_bot':
#                    await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=message_text)
                        message_text = update.message.text.split(' ', 1)[1]

        if update.message.reply_to_message:
            if update.message.reply_to_message['from'].username=='neiropiki_bot':
                    pmsg = r.get(update.message.reply_to_message.message_id)
                    if pmsg:
                        msg = pickle.loads(pmsg)
                        pmsg = r.get(msg.reply_to_message.message_id)
                        msg = pickle.loads(pmsg)
                        message_text = msg.text + '\n' + update.message.text
                        if message_text.split(' ',1)[0]=='@neiropiki_bot':
                            message_text = message_text.split(' ', 1)[1]
                        await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=message_text)
                    else:
                        await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=update.message.reply_to_message.message_id)

        if message_text== '':
            return

        typing_task = context.application.create_task(
            self.send_typing(update, context, every_seconds=4)
        )

        r.set(update.message.message_id,pickle.dumps(update.message))
        send = await context.bot.send_message(chat_id=update.effective_chat.id, text="Got request")
        
        try:
            text = self.ai.create_text(message_text)
        except:
            text = u"Ответ от нейросети не получен"

        if text:
            await context.bot.editMessageText(chat_id=update.effective_chat.id,
                                message_id=send.message_id,
                                text=f"Request done in {text.time_cons} sec")

        send = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.message.message_id,
            text=text.text
        )

        r.set(send.message_id,pickle.dumps(send))

        typing_task.cancel()



    async def send_typing(self, update: Update, context: ContextTypes.DEFAULT_TYPE, every_seconds: int):
        """
        Sends the typing action
        """
        if not self.is_allowed(update.message.from_user.id):
            return

        while True:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            await asyncio.sleep(every_seconds)

    async def gen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Generates text
        """
        if not self.is_allowed(update.message.from_user.id):
            return

        typing_task = context.application.create_task(
            self.send_typing(update, context, every_seconds=4)
        )

        message_text = update.message.text[5:]
        if message_text == "":
            await context.bot.send_message(chat_id=update.effective_chat.id, text="/gen {prompt}")
        else:
            send = await context.bot.send_message(chat_id=update.effective_chat.id, text="Got request")

            try:
                text = self.ai.create_text(message_text)
            except:
                text = u"Ответ от нейросети не получен"

            await context.bot.editMessageText(chat_id=update.effective_chat.id,
                                              message_id=send.message_id,
                                              text=f"Request done in {text.time_cons} sec")

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                reply_to_message_id=update.message.message_id,
                text=text.text
            )

        typing_task.cancel()

    def run(self):
        """
        Run the bot
        """
        application = ApplicationBuilder().token(self.bot_token).build()


        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('gen', self.gen))
        application.add_handler(MessageHandler(filters.TEXT & filters.USER, self.prompt))

        application.run_polling()
