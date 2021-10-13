import configparser
import os

config = configparser.ConfigParser(strict=False, interpolation=None)

try:
    config.read('{}/config.ini'.format(os.path.dirname(os.path.realpath(__file__))))
except TypeError as e:
    print(e)
    exit('Additional field detected on config class.  Please add this in the proper way.')
except Exception:
    exit("Please make sure conf/config.ini is set")


class Config:
    rabbit_user: str
    rabbit_password: str
    host: str
    serial: str

    def __init__(self):
        self.rabbit_password = config.get('VERKLIKKER', 'RABBIT_USER')
        self.rabbit_user = config.get('VERKLIKKER', 'RABBIT_PWD')
        self.serial = config.get('VERKLIKKER', 'SERIAL')
        self.host = config.get('VERKLIKKER', 'HOST')
