import secrets
from sys import argv


def get_new_secret_key(length=256, outfile="secret.key"):
    "Create a file 'outfile' with a secret key of length default to 256"
    hex_token = secrets.token_hex(256)
    with open('secret.key', 'w') as f:
        print(hex_token, file=f)


if __name__ == "__main__":
    if len(argv) == 1:
        get_new_secret_key()
    elif len(argv) == 2:
        arg = argv[1]
        if arg.isdigit():
            get_new_secret_key(length=arg)
        else:
            get_new_secret_key(outfile=arg)
    elif len(argv) == 3:
        arg0 = argv[1]
        arg1 = argv[2]
        if arg0.isdigit() and arg1.isalnum():
            get_new_secret_key(length=arg0, outfile=arg1)
        else:
            print("Wrong arguments! Expected integer followed by a filename")
    else:
        print("Too many arguments!!!")