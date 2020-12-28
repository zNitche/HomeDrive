from passlib.hash import sha256_crypt
import argparse


def main(opt):
    password = sha256_crypt.hash(opt.i)
    print(password)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HomeDrive hash password")
    parser.add_argument("-i", help="password to hash")
    opt = parser.parse_args()

    main(opt)
