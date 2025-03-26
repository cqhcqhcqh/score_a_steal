import hashlib

def calculate_sign(token, t, appKey, data):
    sign_str = f"{token}&{t}&{appKey}&{data}"
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    return sign