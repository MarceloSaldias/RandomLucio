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
    update.message.reply_text("Hola! Ahora puedes mandar canciones con el comando /play")

def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Oa!')

def play(update, context):
    song = " ".join(context.args)
    response = spotify.play(song,first=True)
    update.message.reply_text(response["content"])

def current(update, context):
    response = spotify.get_current_song()
    update.message.reply_text(response['content'])

def set_timer(update, context):
    """Add a job to the queue"""
    chat_id = update.message.chat_id

    # Definimos que el bot se actualizara cada 10 segundos
    timeout = 3
    try:
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        new_job = context.job_queue.run_once(alarm, timeout, context=chat_id)
        context.chat_data['job'] = new_job

        update.message.reply_text('Timer set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')

def help_(update, context):
    update.message.reply_text('/play <nombre cancion> reproduce la cancion\n/current Muestra la  cancion actual\nn.n!')

def unset(update, context):
    """Remove the job if the user changed their mind"""
    if 'job' not in context.chat_data:
        update.message.reply_text('You have no active timer')
        return
    
    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text('Timer successfully unset!')

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
    dp.add_handler(CommandHandler("set", set_timer,
                                   pass_args=True,
                                   pass_job_queue=True,
                                   pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    #log all errors
    dp.add_error_handler(error)

    # Start
    updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()
