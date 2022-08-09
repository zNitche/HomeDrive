# HomeDrive
### Easy to use minimalist file server

---
### Install
1. Clone this repo.
2. Generate `.env` config file and change config values (`STORAGE_*_PATH` and `MYSQL_ROOT_PASSWORD`).
```
python3 generate_dotenv.py
```
3. Run docker container.
```
sudo docker compose up -d
```
4. Bash into container.
```
sudo docker container exec -it home_drive_web_app bash
```
5. Create users accounts using `users_manager.py` (this includes user's permissions settings).

### Dev
1. Change `MYSQL_SERVER_HOST` in `.env` to `127.0.0.1`
2. Run DEV MySQL container.
```
sudo docker compose -f docker-compose-dev.yml up
```

### Usage
1. Use `Shared/Private` switch to switch between shared and private space (if current user has private space)
2. Use `Download/Delete` buttons to manage files (download and delete them)
3. Use `Create Directory` button to create directory inside your private space
4. Use `Upload` button to upload file to shared or private space (or selected directory inside private space)
