from users.users_accounts import UsersAccounts


def delete_permission(username):
    users = UsersAccounts.users
    return users[username]["can_delete_files"]


def private_space_permission(username):
    users = UsersAccounts.users
    return users[username]["have_private_space"]


def can_upload_permission(username):
    users = UsersAccounts.users
    return users[username]["can_upload"]


def max_private_files_size(username):
    users = UsersAccounts.users
    return users[username]["max_files_size"]