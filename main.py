#!/usr/bin/env python
import os
import sys
import threading
from datetime import datetime, timezone

import pika
import telegram_send
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from pytz import timezone

from config import Config

first_message_sent = False
door_closed_timer = None

config = Config()


def door_closed(*args, **kwargs):
    global first_message_sent
    telegram_send.send(messages=[f"Deur gesloten op {args[0]}"])
    first_message_sent = False


def callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body):
    time = datetime.now(tz=timezone('Europe/Amsterdam')).strftime('%Y-%m-%d %H:%M:%S')

    global first_message_sent
    global door_closed_timer

    ch.basic_ack(delivery_tag=method.delivery_tag)

    if first_message_sent is False:
        telegram_send.send(messages=[f"Deur open op {time}"])
        door_closed_timer = threading.Timer(3.5, door_closed, [time])
        first_message_sent = True
    else:
        door_closed_timer.cancel()
        door_closed_timer = threading.Timer(3.5, door_closed, [time])

    door_closed_timer.start()


def main():
    credentials = pika.PlainCredentials(config.rabbit_user, config.rabbit_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config.host,
                                  credentials=credentials))

    channel = connection.channel()
    result = channel.queue_declare(exclusive=False, queue="wake_up")
    channel.queue_bind(result.method.queue,
                       exchange="amq.topic",
                       routing_key=f".{config.serial}.io1_wake_up")

    channel.basic_consume(on_message_callback=callback, queue=result.method.queue)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        exit(0)
