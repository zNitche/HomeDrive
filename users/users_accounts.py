import json
from config import Config


class UsersAccounts:
    CURRENT_DIR = Config.CURRENT_DIR

    with open(f"{CURRENT_DIR}/users/users.json", "r") as accounts:
        users = json.loads(accounts.read())
