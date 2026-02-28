from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from db import query_one, query_all, execute

app = Flask(__name__)
app.secret_key = "cambia_esto_por_una_clave_larga_123456"

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Tienes que iniciar sesión.")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper

# PARTE PÚBLICA
@app.route("/")
def home():
    posts = query_all("""
        SELECT posts.id, posts.title, posts.content, posts.created_at, users.username
        FROM posts
        JOIN users ON users.id = posts.user_id
        ORDER BY posts.created_at DESC
        LIMIT 20
    """)
    return render_template("home.html", posts=posts)

@app.route("/about")
def about():
    return render_template("about.html")

# REGISTRO
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Rellena todos los campos.")
            return redirect(url_for("register"))

        existing = query_one("SELECT id FROM users WHERE username=%s OR email=%s", (username, email))
        if existing:
            flash("Usuario o email ya existe.")
            return redirect(url_for("register"))

        pwd_hash = generate_password_hash(password)
        execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, pwd_hash)
        )

        flash("Registro OK. Ya puedes hacer login.")
        return redirect(url_for("login"))

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = query_one("SELECT * FROM users WHERE username=%s", (username,))
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Credenciales incorrectas.")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash("Login OK.")
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.")
    return redirect(url_for("home"))

# PARTE PRIVADA
@app.route("/dashboard")
@login_required
def dashboard():
    posts = query_all("""
        SELECT id, title, content, created_at
        FROM posts
        WHERE user_id=%s
        ORDER BY created_at DESC
    """, (session["user_id"],))
    return render_template("dashboard.html", posts=posts)

# 3er FORMULARIO (crear post)
@app.route("/add", methods=["GET", "POST"])
@login_required
def add_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Rellena título y contenido.")
            return redirect(url_for("add_post"))

        execute(
            "INSERT INTO posts (user_id, title, content) VALUES (%s, %s, %s)",
            (session["user_id"], title, content)
        )
        flash("Post creado.")
        return redirect(url_for("dashboard"))

    return render_template("add_post.html")

if __name__ == "__main__":
    app.run(debug=True)
