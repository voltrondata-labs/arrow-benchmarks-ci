import os

from config import Config

file = open("env", "w")

for key in Config.__dict__.keys():
    if key.startswith("_"):
        continue
    if os.getenv(key):
        file.write(f"{key}={os.getenv(key)}\n")

file.close()
