"""
Simple Bot to send timed Telegram messages.

This Bot uses the Application class to handle the bot and the JobQueue to send
timed messages.

First, a few handler functions are defined. Then, those functions are passed
to the Application and registered at their respective places.
Then, the bot is started and runs until we press CTRL-C on the cmd.

Usage:
Basic Alarm Bot example, sends a message after a set time.
Press CTRL-C on the cmd.

Note:
To use the JobQueue, you must install PTB via
`pip install "python-telegram-bot[job-queue]"`
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

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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
async def start (update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  # Sends explanation on how to use the bot.
  await update.message.reply_text("Hi! Use /set <seconds> to set a time")

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
  # Send the alarm message.
  job = context.job
  await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
  # Remove job with given name. Returns whether job was removed.
  current_jobs = context.job_queue.get_jobs_by_name(name)
  if not current_jobs:
    return False
  for job in current_jobs:
    job.schedule_removal()
  return True

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  # Add a job to the queue
  chat_id = update.effective_message.chat_id
  try:
    # args[0] should contain the time for the timer in seconds
    due = float(context.args[0])
    if due < 0:
      await update.effective_message.reply_text("Sorry we can not go back to the future!")
      return
    
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

    text = "Timer successfully set!"
    if job_removed:
      text += " Old one was removed."
    await update.effective_message.reply_text(text)
  except (IndexError, ValueError):
    await update.effective_message.reply_text("Usage: /set <seconds>")

async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  # Remove the job if the user changed their mind.
  chat_id = update.message.chat_id
  job_removed = remove_job_if_exists(str(chat_id), context)
  text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
  await update.message.reply_text(text)

def main() -> None:
  # Start the bot.
  # Create the Application and pass your bot's token
  print('Starting bot...')
  app = Application.builder().token(TOKEN).build()

  # Commands
  app.add_handler(CommandHandler(["start", "help"], start))
  app.add_handler(CommandHandler("set", set_timer))
  app.add_handler(CommandHandler("unset", unset))

  # Run the bot until the user presses CTRL-C
  app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
  main()