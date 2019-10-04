import re

invalid_escape = re.compile(r'\\[0-7]{1,3}')  # up to 3 digits for byte values up to FF


def replace_with_byte(match):
    return chr(int(match.group(0)[1:], 8))


def repair(brokenjson):
    return invalid_escape.sub(replace_with_byte, brokenjson.encode('utf8').replace(b'\u000', '').decode('utf8'))
