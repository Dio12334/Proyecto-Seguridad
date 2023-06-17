import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()  # Generate a random salt
    hashed_password = bcrypt.hashpw(password.encode(), salt)  # Hash the password with the salt
    return hashed_password

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password)
