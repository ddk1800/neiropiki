FROM pypy:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY chatGPT.py ./
COPY telegramBot.py ./
COPY main.py ./

ENV TELEGRAM_BOT_TOKEN=1
ENV OPENAI_API_TOKEN=1
ENV USER_ALLOWED=1

CMD [ "pypy3", "./main.py" ]