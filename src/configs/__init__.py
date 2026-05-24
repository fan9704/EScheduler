from src.configs.db import TortoiseSettings
from src.configs.cfg import *
from src.configs.jwt import *
from src.configs.openapi import *
from src.configs.rabbitmq import *
from src.configs.smtp import *

tortoise_config = TortoiseSettings.generate()
