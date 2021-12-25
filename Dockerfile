FROM ubuntu:latest

RUN apt update && apt-get -y install python3 python3-pip && pip3 install requests aiogram pandas
RUN pip3 install tqdm bs4
COPY . .
CMD ["python3", "bot.py"]
