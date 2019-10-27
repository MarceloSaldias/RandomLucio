from telegram.ext import Updater, CommandHandler
import logging
from spotify import Spotify
from keys import CLIENT_ID, TELEGRAM_BOT_KEY
import json

spotify = Spotify(CLIENT_ID)
# ESTO ES TEMPORAL 
with open('auth_spot.json', 'r') as file:
    spotify.token_info = json.load(file)
# -----------------


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text("Bienvenido! :D\n/play <nombre cancion> reproduce la cancion\n/current Muestra la cancion actual\nn.n!")

def play(update, context):
    song = " ".join(context.args)
    response = spotify.play(song,first=True)
    update.message.reply_text(response["content"])
    logging.info('Called /play "%s"', update)

def current(update, context):
    response = spotify.get_current_song()
    update.message.reply_text(response['content'])
    logging.info('Called /current "%s"', update)

def help_(update, context):
    update.message.reply_text('/play <nombre cancion> reproduce la cancion\n/current Muestra la  cancion actual\nn.n!')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Run bot."""
    updater = Updater(TELEGRAM_BOT_KEY, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_))
    dp.add_handler(CommandHandler("play", play, pass_args=True))
    dp.add_handler(CommandHandler("current", current))

    #log all errors
    dp.add_error_handler(error)

    # Start
    updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()
