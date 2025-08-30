import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "database.db"

# Configuração do admin
NOME = "Administrador"
EMAIL = "admin@test.com"
SENHA = "admin"   # <- senha padrão (pode mudar aqui)
TIPO = "admin"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# Apaga qualquer admin existente
cur.execute("DELETE FROM usuarios WHERE email = ?", (EMAIL,))

# Insere novamente com senha já criptografada
cur.execute(
    "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
    (NOME, EMAIL, generate_password_hash(SENHA), TIPO),
)

conn.commit()
conn.close()

print("✅ Usuário admin resetado com sucesso!")
print(f"Login: {EMAIL}")
print(f"Senha: {SENHA}")
