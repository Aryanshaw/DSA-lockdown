import hashlib

p = input("Set emergency passphrase: ")
h = hashlib.sha256(p.encode()).hexdigest()
open("secret.hash", "w").write(h)
print("Saved.")
