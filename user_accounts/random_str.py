import random
import string

def get_random_str(length):
    letters = string.ascii_uppercase + string.digits
    return (''.join(random.choice(letters) for i in range(length)))