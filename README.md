# HomeDrive
### Easy to use minimalist file server

---
## App + MySQL Setup:
### Install
1. Clone this repo.
2. Generate `.env` config file and change config values (`STORAGE_*_PATH` and `MYSQL_ROOT_PASSWORD`).
```
python3 generate_dotenv.py --db_mode MySQL
```
3. Run docker container.
```
sudo docker compose -f docker-compose.yml up -d
```

### Dev
1. Change `MYSQL_SERVER_HOST` in `.env` to `127.0.0.1`
2. Run DEV docker-compose.
```
sudo docker compose -f docker-compose-dev.yml up
```

## App + SQLite Setup:
### Install
1. Clone this repo.
2. Generate `.env` config file and change config values (`STORAGE_*_PATH`).
```
python3 generate_dotenv.py --db_mode SQLite
```
3. Run docker container.
```
sudo docker compose -f docker-compose-sqlite.yml up -d
```

### Dev
just run app
```
python3 app.py
```

## Create accounts
1. Bash into container.
```
sudo docker container exec -it home_drive_web_app bash
```
2. Create users accounts using `users_manager.py` (this includes user's permissions settings).


### Usage
1. Use `Shared/Private` switch to switch between shared and private space (if current user has private space)
2. Use `Download/Delete` buttons to manage files (download and delete them)
3. Use `Create Directory` button to create directory inside your private space
4. Use `Upload` button to upload file to shared or private space (or selected directory inside private space)
