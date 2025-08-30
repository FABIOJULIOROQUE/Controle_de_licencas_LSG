import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "topzera"

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------- LOGIN ----------------------
@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email=?", (email,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user["senha"], senha):
            session["user_id"] = user["id"]
            session["nome"] = user["nome"]
            session["tipo"] = user["tipo"]
            if user["tipo"] == "admin":
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("dashboard"))
        else:
            flash("Email ou senha inválidos!", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------- DASHBOARD ----------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    uid = session["user_id"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, responsavel, representante, estado, tipo,
               codigo_licenca, codigo_manutencao, licenca, descricao, novo_codigo, data_import
        FROM licencas
        WHERE user_id IN (
            SELECT user_id FROM usuario_licencas WHERE usuario_id=?
        )
    """, (uid,))
    licencas = cur.fetchall()
    conn.close()

    return render_template("dashboard.html", licencas=licencas)


# ---------------------- ADMIN ----------------------
@app.route("/admin")
def admin():
    if "tipo" not in session or session["tipo"] != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, responsavel, representante, estado, tipo, codigo_licenca FROM licencas ORDER BY id DESC LIMIT 10")
    licencas = cur.fetchall()
    conn.close()
    return render_template("admin.html", licencas=licencas)


# ---------------------- USERS CRUD ----------------------
@app.route("/admin/users")
def admin_users():
    if "tipo" not in session or session["tipo"] != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()
    conn.close()
    return render_template("admin_users.html", usuarios=usuarios)


@app.route("/admin/users/new", methods=["GET", "POST"])
def admin_users_new():
    if "tipo" not in session or session["tipo"] != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    # Opções únicas vindas da planilha de licenças
    cur.execute("SELECT DISTINCT representante FROM licencas WHERE representante IS NOT NULL")
    representantes = [r["representante"] for r in cur.fetchall()]

    cur.execute("SELECT DISTINCT estado FROM licencas WHERE estado IS NOT NULL")
    estados = [e["estado"] for e in cur.fetchall()]

    cur.execute("SELECT DISTINCT cidade FROM licencas WHERE cidade IS NOT NULL")
    cidades = [c["cidade"] for c in cur.fetchall()]

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])
        tipo = request.form["tipo"]
        representante = request.form.get("representante")
        estado = request.form.get("estado")
        cidade = request.form.get("cidade")

        cur.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo, representante, estado, cidade) VALUES (?,?,?,?,?,?,?)",
            (nome, email, senha, tipo, representante, estado, cidade),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("admin_users"))

    conn.close()
    return render_template("admin_users_new.html", representantes=representantes, estados=estados, cidades=cidades)


@app.route("/admin/users/<int:id>/edit", methods=["GET", "POST"])
def admin_users_edit(id):
    if "tipo" not in session or session["tipo"] != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id=?", (id,))
    usuario = cur.fetchone()

    cur.execute("SELECT DISTINCT representante FROM licencas WHERE representante IS NOT NULL")
    representantes = [r["representante"] for r in cur.fetchall()]

    cur.execute("SELECT DISTINCT estado FROM licencas WHERE estado IS NOT NULL")
    estados = [e["estado"] for e in cur.fetchall()]

    cur.execute("SELECT DISTINCT cidade FROM licencas WHERE cidade IS NOT NULL")
    cidades = [c["cidade"] for c in cur.fetchall()]

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        tipo = request.form["tipo"]
        representante = request.form.get("representante")
        estado = request.form.get("estado")
        cidade = request.form.get("cidade")

        cur.execute(
            "UPDATE usuarios SET nome=?, email=?, tipo=?, representante=?, estado=?, cidade=? WHERE id=?",
            (nome, email, tipo, representante, estado, cidade, id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("admin_users"))

    conn.close()
    return render_template("admin_users_edit.html", usuario=usuario, representantes=representantes, estados=estados, cidades=cidades)


@app.route("/admin/users/<int:id>/delete")
def admin_users_delete(id):
    if "tipo" not in session or session["tipo"] != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_users"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
