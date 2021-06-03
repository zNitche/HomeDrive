# HomeDrive
### Easy to use minimalist file server

---
### Install
1. Clone this repo
2. Create users accounts using `manage_users.py` (this includes user's permissions settings)
3. Build docker image `sudo docker build -t homedrive .`
4. Run docker container
```
sudo docker run --name=homedrive -d -v <path_to_files_storage> -p 8080:8080 homedrive
```
5. Make docker container restart after reboot `sudo docker update --restart unless-stopped homedrive`

### Usage
1. Login (Test user creds: `login = user | password = test`)
2. Use `Shared/Private` switch to switch between shared and private space (if current user has private space)
3. Use `Download/Delete` buttons to manage files (download and delete them)
4. Use `Upload` button to upload file to shared or private space