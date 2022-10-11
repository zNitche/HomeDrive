import multiprocessing
from config import Config


bind = f"{Config.APP_HOST}:{Config.APP_PORT}"

workers = multiprocessing.cpu_count() - 1
threads = 1
worker_class = "gthread"
worker_connections = 1000

timeout = 20
keepalive = 1
