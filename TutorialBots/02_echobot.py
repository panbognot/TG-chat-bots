"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press CTRL-C on the cmd.

Usage:
Basic Echobot example, repeats messages.
Press CTRL-C on the cmd to stop the bot.
"""
import logging
import tgkeys
from telegram import __version__ as TG_VER

try:
  from telegram import __version_info__
except ImportError:
  __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

# Note: This apparently needs to be checked regular since they update the
#   library pretty often.
if __version_info__ < (20, 0, 0, "alpha", 1):
  raise RuntimeError(
    f"This example is not compatible with your current PTB version {TG_VER}."
  )

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = tgkeys.TOKEN
BOT_USERNAME = tgkeys.BOT_USERNAME

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

### START of the ACTUAL BOT CODE! ###
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  # Send a message when the command /start is issued.
  user = update.effective_user
  await update.message.reply_html(
    rf"Hi {user.mention_html()}!",
    reply_markup=ForceReply(selective=True),
  )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  # Send a message when the command /help is issued.
  await update.message.reply_text("Help!")

async def echo_feature(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  # Echo the user message.
  await update.message.reply_text(update.message.text)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
  print(f'Update {update} caused error {context.error}')

def main() -> None:
  # Start the bot.
  # Create the Application and pass your bot's token
  print('Starting bot...')
  app = Application.builder().token(TOKEN).build()

  # Commands
  app.add_handler(CommandHandler("start", start_command))
  app.add_handler(CommandHandler("help", help_command))

  # Echo messages on non-commands
  app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_feature))

  # Errors
  app.add_error_handler(error)

  # Run the bot until the user presses CTRL-C
  app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
  main()