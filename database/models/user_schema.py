import time


def create_user_doc(username, email, password_hash, wallet):
    return {
        "username": username,
        "email": email,
        "password": password_hash,
        "wallet": wallet,
        "created_at": time.time(),
        "is_active": True,
    }
