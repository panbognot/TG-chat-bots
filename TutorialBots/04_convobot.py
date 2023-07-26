"""
First, a few callback functions are defined. Then, those functions are passed to
the App and registered at their respective places.
Then, the bot is started and runs until we press CTRL-C.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press CTRL-C to stop.
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
if __version_info__ < (20, 0, 0, "alpha", 5):
  raise RuntimeError(
    f"This example is not compatible with your current PTB version {TG_VER}."
  )

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
  Application, 
  CommandHandler, 
  ContextTypes, 
  ConversationHandler,
  MessageHandler, 
  filters,
)

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
GENDER, PHOTO, LOCATION, BIO = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  # Starts the converesation and asks the user about their gender.
  reply_keyboard = [["Boy", "Girl", "Other"]]

  await update.message.reply_text(
    "Hi! My name is Professor Bot. I will hold a conversation with you. "
    "Send /cancel to stop talking to me.\n\n"
    "Are you a boy or a girl?",
    reply_markup=ReplyKeyboardMarkup(
      reply_keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl?"
    ),
  )

  return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  # Stores the selected gender and asks for a photo
  user = update.message.from_user
  logger.info("Gender of %s: %s", user.first_name, update.message.text)
  await update.message.reply_text(
    "I see! Please send me a photo of yourself, "
    "so I know what you look like, or send /skip if you don't want to.",
    reply_markup=ReplyKeyboardRemove(),
  )

  return PHOTO

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  # Stores the photo and asks for a location.
  user = update.message.from_user
  photo_file = await update.message.photo[-1].get_file()
  await photo_file.download_to_drive("user_photo.jpg")
  logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
  await update.message.reply_text(
    "Gorgeous! Now, send me your location please, or send /skip if you don't want to."
  )

  return LOCATION

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  # Skips the photo and asks for a location.
  user = update.message.from_user
  logger.info("User %s did not send a photo.", user.first_name)
  await update.message.reply_text(
    "I bet you look great! Now, send me your location please, or send /skip."
  )

  return LOCATION

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  # Stores the location and asks for some info about the user.
  user = update.message.from_user
  user_location = update.message.location
  logger.info(
    "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
  )
  await update.message.reply_text(
    "Maybe I can visit you sometime! At last, tell me something about yourself."
  )

  return BIO

# TODO: still lots of things to type