FROM python:3
ADD bot.py /
ADD keys.py /
ADD spotify.py /
ADD auth_spot.json /
RUN pip install requests python-telegram-bot
CMD ["python", "./bot.py"]
