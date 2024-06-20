import pickle
from pathlib import Path
import bcrypt

names = ["Kamil", "Beata"]
usernames = ["kkamil","bbeata"]
passwords = ["XXX", "XXX"]

# Hashowanie haseł
hashed_passwords = [bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') for password in passwords]

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)
