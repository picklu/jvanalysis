import secrets

hex_token = secrets.token_hex(256)
with open('secret.key', 'w') as f:
    print(hex_token, file=f)
