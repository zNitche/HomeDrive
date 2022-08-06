from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, can_delete_files, have_private_space, can_upload):
        super().__init__()
        self.can_delete_files = can_delete_files
        self.have_private_space = have_private_space
        self.can_upload = can_upload
