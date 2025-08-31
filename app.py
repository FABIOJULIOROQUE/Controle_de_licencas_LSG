import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_NAME = "database.db"
EXCEL_FILE = "Kion South America All Active Licenses.xlsx"


# =========================
# Conexão
# =========================
def get_db():
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row
    return con


# =========================
# Logs
# =========================
def registrar_log(usuario, acao):
    con = get_db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO logs (usuario, acao, data_hora)
        VALUES (?, ?, datetime('now','localtime'))
    """, (usuario, acao))
    con.commit()
    con.close()


# =========================
# Importar Licenças do Excel
# =========================
def import_licencas_from_excel():
    if not os.path.exists(EXCEL_FILE):
        print("⚠️ Arquivo de licenças não encontrado:", EXCEL_FILE)
        return

    con = get_db()
    cur = con.cursor()
    cur.execute("DELETE FROM licencas")

    df = pd.read_excel(EXCEL_FILE)

    for _, row in df.iterrows():
        user_id = row.get("User ID") or row.get("User Id")
        responsavel = row.get("Responsável")
        setor = row.get("Setor")
        representante = row.get("Representante")
        cidade = row.get("Cidade")
        estado = row.get("Estado")
        tipo = row.get("Tipo")
        nome_computador = (
            row.get("Nome do computador")
            or row.get("Computador")
            or row.get("Nome Computador")
        )
        codigo_manutencao = (
            row.get("Codigo Manutenção")
            or row.get("Código Manutenção")
            or row.get("NovoCodigoReq")
            or row.get("CodManNovoReq")
        )

        if not (user_id or responsavel or codigo_manutencao):
            continue

        cur.execute("""
            INSERT INTO licencas (
                user_id, responsavel, setor, representante, cidade, estado, tipo,
                codigo_manutencao, nome_computador, data_import
            )
            VALUES (?,?,?,?,?,?,?,?,?,date('now'))
        """, (
            user_id, responsavel, setor, representante, cidade, estado, tipo,
            codigo_manutencao, nome_computador
        ))

    con.commit()
    con.close()
    print("✅ Licenças importadas/atualizadas com sucesso!")


# =========================
# Login / Logout
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        senha = request.form["senha"]

        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        user = cur.fetchone()

        if user and check_password_hash(user["senha"], senha):
            session["user_id"] = user["id"]
            session["user_tipo"] = user["tipo"]
            session["user_nome"] = user["nome"]

            registrar_log(user["nome"], "Login realizado")
            flash(f"✅ Bem-vindo, {user['nome']}!", "success")
            return redirect(url_for("admin" if user["tipo"] == "admin" else "dashboard"))
        else:
            flash("❌ E-mail ou senha inválidos.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    if session.get("user_nome"):
        registrar_log(session.get("user_nome"), "Logout realizado")
    session.clear()
    flash("✅ Logout realizado com sucesso.", "success")
    return redirect(url_for("login"))


# =========================
# Painel Admin
# =========================
@app.route("/admin")
def admin():
    if session.get("user_tipo") != "admin":
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()
    cur.execute("""
        SELECT user_id, responsavel, setor, representante, cidade, estado, tipo,
               codigo_manutencao, nome_computador
        FROM licencas
        ORDER BY id DESC
    """)
    licencas = cur.fetchall()

    return render_template("admin.html", licencas=licencas)


# =========================
# Usuários (CRUD)
# =========================
@app.route("/admin/users")
def admin_users():
    if session.get("user_tipo") != "admin":
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()
    cur.execute("""
        SELECT * FROM usuarios
        ORDER BY 
            CASE WHEN tipo = 'admin' THEN 0 ELSE 1 END,
            nome ASC
    """)
    usuarios = cur.fetchall()
    return render_template("admin_users.html", usuarios=usuarios)


@app.route("/admin/users/new", methods=["GET", "POST"])
def admin_users_new():
    if session.get("user_tipo") != "admin":
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()

    representantes = [r[0] for r in cur.execute("SELECT DISTINCT representante FROM licencas WHERE representante IS NOT NULL").fetchall()]
    estados = [r[0] for r in cur.execute("SELECT DISTINCT estado FROM licencas WHERE estado IS NOT NULL").fetchall()]
    cidades = [r[0] for r in cur.execute("SELECT DISTINCT cidade FROM licencas WHERE cidade IS NOT NULL").fetchall()]

    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip()
        senha = request.form["senha"]
        tipo = request.form["tipo"]
        representante = request.form.get("representante")
        estado = request.form.get("estado")
        cidade = request.form.get("cidade")

        # 🔒 Regra: apenas admin pode usar "Todos"
        if session.get("user_tipo") != "admin":
            if representante == "Todos" or estado == "Todos" or cidade == "Todos":
                flash("❌ Apenas administradores podem definir 'Todos'.", "danger")
                return redirect(url_for("admin_users_edit", user_id=user_id))


        if not email:
            flash("❌ O campo e-mail é obrigatório.", "danger")
            return redirect(url_for("admin_users_new"))

        senha_hash = generate_password_hash(senha)

        try:
            cur.execute("""
                INSERT INTO usuarios (nome, email, senha, tipo, representante, estado, cidade)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nome, email, senha_hash, tipo, representante, estado, cidade))
            con.commit()

            registrar_log(session.get("user_nome"), f"Criou usuário: {nome}")
            flash("✅ Usuário criado com sucesso!", "success")
            return redirect(url_for("admin_users"))
        except sqlite3.IntegrityError:
            flash("❌ Já existe um usuário com este e-mail.", "danger")
            return redirect(url_for("admin_users_new"))

    return render_template("admin_users_form.html",
                           representantes=representantes,
                           estados=estados,
                           cidades=cidades)


@app.route("/admin/users/edit/<int:user_id>", methods=["GET", "POST"])
def admin_users_edit(user_id):
    if session.get("user_tipo") != "admin":
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id=?", (user_id,))
    usuario = cur.fetchone()

    if not usuario:
        flash("❌ Usuário não encontrado.", "danger")
        return redirect(url_for("admin_users"))

    representantes = [r[0] for r in cur.execute("SELECT DISTINCT representante FROM licencas WHERE representante IS NOT NULL").fetchall()]
    estados = [r[0] for r in cur.execute("SELECT DISTINCT estado FROM licencas WHERE estado IS NOT NULL").fetchall()]
    cidades = [r[0] for r in cur.execute("SELECT DISTINCT cidade FROM licencas WHERE cidade IS NOT NULL").fetchall()]

    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip()
        tipo = request.form["tipo"]
        representante = request.form.get("representante")
        estado = request.form.get("estado")
        cidade = request.form.get("cidade")

        # 🔒 Apenas admin pode usar "Todos"
        if session.get("user_tipo") != "admin":
            if representante == "Todos" or estado == "Todos" or cidade == "Todos":
                flash("❌ Apenas administradores podem definir 'Todos'.", "danger")
                return redirect(url_for("admin_users_edit", user_id=user_id))

        if request.form.get("senha"):  # Se foi digitada nova senha
            senha_hash = generate_password_hash(request.form["senha"])
            cur.execute("""
                UPDATE usuarios
                SET nome=?, email=?, tipo=?, representante=?, estado=?, cidade=?, senha=?
                WHERE id=?
            """, (nome, email, tipo, representante, estado, cidade, senha_hash, user_id))
        else:
            cur.execute("""
                UPDATE usuarios
                SET nome=?, email=?, tipo=?, representante=?, estado=?, cidade=?
                WHERE id=?
            """, (nome, email, tipo, representante, estado, cidade, user_id))

        con.commit()
        con.close()

        registrar_log(session.get("user_nome"), f"Editou usuário ID: {user_id}")
        flash("✅ Usuário atualizado com sucesso!", "success")
        return redirect(url_for("admin_users"))

    return render_template("admin_users_form.html",
                           usuario=usuario,
                           representantes=representantes,
                           estados=estados,
                           cidades=cidades)

@app.route("/admin/users/delete/<int:user_id>")
def admin_users_delete(user_id):
    if session.get("user_tipo") != "admin":
        flash("❌ Acesso negado.", "danger")
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()
    cur.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
    con.commit()
    con.close()

    registrar_log(session.get("user_nome"), f"Excluiu usuário ID: {user_id}")
    flash("✅ Usuário excluído com sucesso!", "success")
    return redirect(url_for("admin_users"))


# =========================
# Dashboard Usuário
# =========================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    con = get_db()
    cur = con.cursor()

    if session.get("user_tipo") == "admin":
        cur.execute("""
            SELECT l.user_id, l.responsavel, l.setor, l.representante, l.cidade,
                   l.estado, l.tipo, l.codigo_manutencao, l.nome_computador
            FROM licencas l
            ORDER BY l.id DESC
        """)
        licencas = cur.fetchall()
        return render_template("dashboard.html", licencas=licencas)

    cur.execute("SELECT representante, estado, cidade FROM usuarios WHERE id=?", (user_id,))
    usuario = cur.fetchone()

    cur.execute("""
        SELECT l.user_id, l.responsavel, l.setor, l.representante, l.cidade,
               l.estado, l.tipo, l.codigo_manutencao, l.nome_computador
        FROM licencas l
        WHERE l.representante = ?
          AND (? IS NULL OR ? = '' OR l.estado = ?)
          AND (? IS NULL OR ? = '' OR l.cidade = ?)
    """, (
        usuario["representante"],
        usuario["estado"], usuario["estado"], usuario["estado"],
        usuario["cidade"], usuario["cidade"], usuario["cidade"]
    ))
    licencas = cur.fetchall()

    return render_template("dashboard.html", licencas=licencas)


# =========================
# Exportar Licenças
# =========================
@app.route("/export_licencas")
def export_licencas():
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()

    if session.get("user_tipo") == "admin":
        cur.execute("""
            SELECT user_id, responsavel, setor, representante, cidade, estado, tipo,
                   codigo_manutencao, nome_computador
            FROM licencas
            ORDER BY id DESC
        """)
    else:
        cur.execute("SELECT representante, estado, cidade FROM usuarios WHERE id=?", (session["user_id"],))
        usuario = cur.fetchone()

        cur.execute("""
            SELECT l.user_id, l.responsavel, l.setor, l.representante, l.cidade,
                   l.estado, l.tipo, l.codigo_manutencao, l.nome_computador
            FROM licencas l
            WHERE l.representante = ?
              AND (? IS NULL OR ? = '' OR l.estado = ?)
              AND (? IS NULL OR ? = '' OR l.cidade = ?)
        """, (
            usuario["representante"],
            usuario["estado"], usuario["estado"], usuario["estado"],
            usuario["cidade"], usuario["cidade"], usuario["cidade"]
        ))

    licencas = cur.fetchall()
    con.close()

    df = pd.DataFrame(licencas, columns=licencas[0].keys() if licencas else [])

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Licencas")

    output.seek(0)
    filename = f"licencas_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    registrar_log(session.get("user_nome"), "Exportou licenças")
    return send_file(output,
                     as_attachment=True,
                     download_name=filename,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# =========================
# Exportar Usuários
# =========================
@app.route("/export_usuarios")
def export_usuarios():
    if session.get("user_tipo") != "admin":
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()
    cur.execute("""
        SELECT id, nome, email, tipo, representante, estado, cidade
        FROM usuarios
        ORDER BY id ASC
    """)
    usuarios = cur.fetchall()
    con.close()

    df = pd.DataFrame(usuarios, columns=usuarios[0].keys() if usuarios else [])

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Usuarios")

    output.seek(0)
    filename = f"usuarios_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    registrar_log(session.get("user_nome"), "Exportou usuários")
    return send_file(output,
                     as_attachment=True,
                     download_name=filename,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# =========================
# Upload de Nova Planilha Excel
# =========================
@app.route("/upload_excel", methods=["POST"])
def upload_excel():
    if session.get("user_tipo") != "admin":
        return redirect(url_for("login"))

    if "file" not in request.files:
        flash("❌ Nenhum arquivo enviado.", "danger")
        return redirect(url_for("admin"))

    file = request.files["file"]

    if file.filename == "":
        flash("❌ Arquivo inválido.", "danger")
        return redirect(url_for("admin"))

    if not file.filename.endswith(".xlsx"):
        flash("❌ Apenas arquivos .xlsx são permitidos.", "danger")
        return redirect(url_for("admin"))

    file.save(EXCEL_FILE)
    import_licencas_from_excel()

    registrar_log(session.get("user_nome"), "Upload de nova planilha de licenças")
    flash("✅ Planilha carregada e licenças atualizadas com sucesso!", "success")
    return redirect(url_for("admin"))


# =========================
# Logs no Admin
# =========================
@app.route("/admin/logs")
def admin_logs():
    if session.get("user_tipo") != "admin":
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 200")
    logs = cur.fetchall()
    con.close()

    return render_template("admin_logs.html", logs=logs)

# =========================
# Trocar Senha
# =========================
@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        senha_atual = request.form["senha_atual"]
        nova_senha = request.form["nova_senha"]

        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT senha FROM usuarios WHERE id=?", (session["user_id"],))
        user = cur.fetchone()

        if not user or not check_password_hash(user["senha"], senha_atual):
            flash("❌ Senha atual incorreta.", "danger")
            return redirect(url_for("change_password"))

        nova_hash = generate_password_hash(nova_senha)
        cur.execute("UPDATE usuarios SET senha=? WHERE id=?", (nova_hash, session["user_id"]))
        con.commit()
        con.close()

        registrar_log(session.get("user_nome"), "Alterou a senha")
        flash("✅ Senha alterada com sucesso!", "success")
        return redirect(url_for("dashboard"))

    return render_template("change_password.html")


# =========================
# Inicialização
# =========================
if __name__ == "__main__":
    import_licencas_from_excel()
    app.run(debug=True)
