FROM python:3.11.13
LABEL maintainer="Yuuzi261 lokasu0531@gmail.com"
LABEL description="A Discord bot for Twitter notifications, using tweety-ns module."
LABEL repository="https://github.com/Yuuzi261/Tweetcord"
LABEL license="MIT"
WORKDIR /bot
COPY requirements.txt /bot/
RUN pip install -r requirements.txt
COPY . /bot
CMD ["python", "bot.py"]