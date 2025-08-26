import uuid
import string
import email

ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
           string.digits
ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(ALPHABET))
BASE = len(ALPHABET)
SIGN_CHARACTER = '$'

def num_encode(n):
    if n < 0:
        return SIGN_CHARACTER + num_encode(-n)
    s = []
    while True:
        n, r = divmod(n, BASE)
        s.append(ALPHABET[r])
        if n == 0: break
    return ''.join(reversed(s))

def create_id():
    id = uuid.uuid4()
    return num_encode(int(id))
