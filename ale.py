import random
import string

def generate_password(length=10):
    # Generate a random password
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    password = ''
    has_uppercase = False
    has_lowercase = False
    has_number = False
    has_special = False

    while len(password) < length or not has_uppercase or not has_lowercase or not has_number or not has_special:
        char = random.choice(characters)
        password += char

        if char in string.ascii_uppercase:
            has_uppercase = True
        elif char in string.ascii_lowercase:
            has_lowercase = True
        elif char in string.digits:
            has_number = True
        elif char in string.punctuation:
            has_special = True

    return password

print(generate_password())