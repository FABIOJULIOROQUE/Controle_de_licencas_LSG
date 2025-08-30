import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()

# =========================
# Usuários
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    tipo TEXT NOT NULL DEFAULT 'user',
    representante TEXT,
    estado TEXT,
    cidade TEXT
)
""")

# =========================
# Licenças
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS licencas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    responsavel TEXT,
    setor TEXT,
    representante TEXT,
    cidade TEXT,
    estado TEXT,
    tipo TEXT,
    codigo_manutencao TEXT,
    data_import TEXT,
    FOREIGN KEY (user_id) REFERENCES usuarios (id)
)
""")

# =========================
# Usuário ↔ Licenças
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS usuario_licencas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    licenca_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES usuarios (id),
    FOREIGN KEY (licenca_id) REFERENCES licencas (id),
    UNIQUE(user_id, licenca_id)
)
""")

# =========================
# Usuário ↔ Cidades
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS usuario_cidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    cidade TEXT NOT NULL,
    estado TEXT NOT NULL,
    representante TEXT,
    FOREIGN KEY (user_id) REFERENCES usuarios (id)
)
""")

# =========================
# Log de Acesso
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    email TEXT,
    ip TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action TEXT,
    FOREIGN KEY (user_id) REFERENCES usuarios (id)
)
""")

# =========================
# Admin padrão (se não existir)
# =========================
cur.execute("""
INSERT OR IGNORE INTO usuarios (id, nome, email, senha, tipo)
VALUES (
    1,
    'admin',
    'admin@example.com',
    'pbkdf2:sha256:600000$123456$abcdef...', -- Substitua por hash válido
    'admin'
)
""")

con.commit()
con.close()

print("✅ Banco de dados inicializado com sucesso!")
