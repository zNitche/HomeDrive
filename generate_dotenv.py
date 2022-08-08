import os


def generate(path):
    args = {
        "MYSQL_ROOT_PASSWORD": "test_pass",
        "MYSQL_SERVER_PORT": "3306",
        "MYSQL_SERVER_HOST": "db",
        "DB_NAME": "app_db",
        "DB_PATH": "./database/mysql"
    }

    parsed_args = [f"{key}={args[key]}" for key in args]

    with open(path, "a") as file:
        for line in parsed_args:
            file.write(line)
            file.write("\n")


def main():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    env_path = os.path.join(current_dir, ".env")

    if os.path.exists(env_path):
        print("Removing existing .env file...")

        os.remove(env_path)

    print("Generating .env config file...")

    generate(env_path)

    print("Generated .env config file...")


if __name__ == '__main__':
    main()
