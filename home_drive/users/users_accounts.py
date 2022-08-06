import json
import os
from config import Config


class UsersAccounts:
    users_json_path = os.path.join(Config.APP_DIR_PATH, "users", "users.json")

    with open(users_json_path, "r") as accounts:
        users = json.loads(accounts.read())
