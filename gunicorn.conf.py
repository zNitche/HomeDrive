import multiprocessing
from config import Config


bind = f"{Config.APP_HOST}:{Config.APP_PORT}"
workers = multiprocessing.cpu_count() * 2 + 1
timeout = Config.APP_TIMEOUT
