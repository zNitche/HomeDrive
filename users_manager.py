from home_drive.models import User
from home_drive.utils import db_utils
from consts import DBConsts
import sqlalchemy
import sqlalchemy.orm
import os
import dotenv
from passlib.hash import sha256_crypt
import shutil


class UsersManager:
    def __init__(self):
        self.db_session = None
        self.users_names = []

        self.load_dotenv()
        self.init_db_session()
        self.get_users_names()

    def get_users_names(self):
        with self.db_session() as session:
            for user in session.query(User).all():
                self.users_names.append(user.username)

    def hash_password(self, plain_password):
        password = sha256_crypt.hash(plain_password)

        return password

    def init_db_session(self):
        db_uri = ""

        if os.environ.get("DB_MODE") == DBConsts.SQLITE_DB:
            db_uri, _ = db_utils.setup_sqlite_db()

        elif os.environ.get("DB_MODE") == DBConsts.MYSQL_DB:
            db_uri, _ = db_utils.setup_mysql_db()

        engine = sqlalchemy.create_engine(db_uri)

        self.db_session = sqlalchemy.orm.sessionmaker(engine)

    def load_dotenv(self):
        dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".env"))

    def add_user(self, user_name, password, can_upload, can_delete, have_private_space, private_space_size):
        from config import Config

        if user_name in self.users_names:
            return 0

        encrypted_password = self.hash_password(password)

        user = User(username=user_name, password=encrypted_password, can_delete_files=can_delete,
                    have_private_space=have_private_space, can_upload=can_upload, max_files_size=private_space_size)

        with self.db_session() as session:
            session.add(user)
            session.commit()

        dir_path = os.path.join(Config.PRIVATE_FILES_LOCATION, user_name)

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        return 1

    def delete_user(self, user_name):
        from config import Config

        with self.db_session() as session:
            user = session.query(User).filter_by(username=user_name).first()

            if user:
                session.delete(user)
                session.commit()

            else:
                return 0

            dir_path = os.path.join(Config.PRIVATE_FILES_LOCATION, user_name)

            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)

            return 1


def show_users(users):
    for user_name in users:
        print(user_name)


def conv_string_to_bool(s):
    if s == "true" or s == "True":
        return True

    elif s == "false" or s == "False":
        return False


def main():
    manager = UsersManager()

    print("---HomeDrive---")
    print("Users Manager. Choose what do you want to do: ")
    print("1) Add new user")
    print("2) Delete user")
    print("3) Show users")
    print("4) Exit")

    choice = int(input("> "))

    if choice == 1:
        private_space_size = 0

        os.system("clear")
        print("---Add user---")

        print("Username: ")
        user_name = input("> ")

        print("Password: ")
        password = input("> ")

        print("Can upload files ? true/false: ")
        can_upload = input("> ")
        can_upload = conv_string_to_bool(can_upload)

        print("Can delete files ? true/false: ")
        can_delete = input("> ")
        can_delete = conv_string_to_bool(can_delete)

        print("Have private space ? true/false: ")
        have_private_space = input("> ")
        have_private_space = conv_string_to_bool(have_private_space)

        if have_private_space:
            print("Private space size (in bytes 5000000000 = 5 GB) : ")
            private_space_size = int(input("> "))

        check = manager.add_user(user_name, password, can_upload, can_delete, have_private_space, private_space_size)

        if not check:
            print("User already exists")
        else:
            print("Added user")

        input("\nPress any key to continue")

        main()

    elif choice == 2:
        os.system("clear")
        print("---Delete user---")

        print("Username: ")
        user_name = input("> ")

        check = manager.delete_user(user_name)

        if not check:
            print("User doesn't exist")
        else:
            print("Removed user")

        input("\nPress any key to continue")

        main()

    elif choice == 3:
        show_users(manager.users_names)

        input("\nPress any key to continue")

        main()

    elif choice == 4:
        return
    else:
        os.system("clear")

        print("Unknown option")
        input("\nPress any key to continue")

        main()


if __name__ == '__main__':
    main()
