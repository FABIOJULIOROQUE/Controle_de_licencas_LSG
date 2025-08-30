# reset_password.py
import sqlite3, sys
from werkzeug.security import generate_password_hash

if len(sys.argv) != 3:
    print("Uso: python reset_password.py <usuario> <nova_senha>")
    sys.exit(1)

user, newpass = sys.argv[1], sys.argv[2]
conn = sqlite3.connect("database.db")
cur = conn.cursor()
cur.execute("UPDATE usuarios SET senha=? WHERE nome=? COLLATE NOCASE",
            (generate_password_hash(newpass), user))
if cur.rowcount == 0:
    print(f"Usuário '{user}' não encontrado.")
else:
    print(f"Senha do usuário '{user}' atualizada.")
conn.commit()
conn.close()

