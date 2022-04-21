import json
from config import Config
import os
import shutil
from passlib.hash import sha256_crypt


def hash_password(plain_password):
    password = sha256_crypt.hash(plain_password)

    return password


def load_users():
    with open(os.path.join(Config.CURRENT_DIR, "users", "users.json"), "r") as accounts:
        users = json.loads(accounts.read())

    return users


def save_to_json(users):
    with open(os.path.join(Config.CURRENT_DIR, "users", "users.json"), "w") as accounts:
        accounts.write(json.dumps(users, indent=4))


def add_user(user_name, password, can_upload, can_delete, have_private_space, private_space_size, is_admin):
    if user_name in load_users():
        return 0

    users = load_users()
    encrypted_password = hash_password(password)

    users[user_name] = {"password": encrypted_password, "have_private_space": have_private_space,
                        "can_delete_files": can_delete, "can_upload": can_upload, "max_files_size": private_space_size,
                        "admin": is_admin}

    save_to_json(users)

    dir_path = os.path.join(Config.PRIVATE_FILES_LOCATION, user_name)

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    return 1


def delete_user(user_name):
    users = load_users()

    if user_name not in users:
        return 0

    del users[user_name]

    dir_path = os.path.join(Config.PRIVATE_FILES_LOCATION, user_name)

    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

    save_to_json(users)

    return 1


def show_users():
    users = load_users()

    for user_name in users:
        print(user_name)


def conv_to_bool(s):
    if s == "true" or s == "True":
        return True
    elif s == "false" or s == "False":
        return False


def main():
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
        can_upload = conv_to_bool(can_upload)

        print("Can delete files ? true/false: ")
        can_delete = input("> ")
        can_delete = conv_to_bool(can_delete)

        print("Is admin ? true/false: ")
        is_admin = input("> ")
        is_admin = conv_to_bool(is_admin)

        print("Have private space ? true/false: ")
        have_private_space = input("> ")
        have_private_space = conv_to_bool(have_private_space)

        if have_private_space:
            print("Private space size (in bytes 5000000000 = 5 GB) : ")
            private_space_size = int(input("> "))

        check = add_user(user_name, password, can_upload, can_delete, have_private_space, private_space_size, is_admin)

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

        check = delete_user(user_name)

        if not check:
            print("User doesn't exist")
        else:
            print("Removed user")

        input("\nPress any key to continue")
        main()

    elif choice == 3:
        show_users()
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
