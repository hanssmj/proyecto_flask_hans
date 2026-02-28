from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import db
import mysql.connector

app = Flask(__name__)
app.secret_key = "cambia-esto-por-una-clave-larga"


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Tienes que hacer login.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


@app.get("/")
def home():
    posts = db.query_all("""
        SELECT p.id, p.title, p.content, p.created_at, u.username
        FROM posts p
        JOIN users u ON u.id = p.user_id
        ORDER BY p.created_at DESC
        LIMIT 12
    """)
    return render_template("home.html", posts=posts)


@app.get("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Rellena todos los campos.", "danger")
            return redirect(url_for("register"))

        pw_hash = generate_password_hash(password)

        try:
            db.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, pw_hash)
            )
            flash("Cuenta creada. Ya puedes hacer login.", "success")
            return redirect(url_for("login"))
        except mysql.connector.IntegrityError:
            flash("Usuario o email ya existe.", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        user = db.query_one(
            "SELECT * FROM users WHERE username=%s OR email=%s",
            (identifier, identifier.lower())
        )
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Credenciales incorrectas.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash("Login OK.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.get("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("home"))


@app.get("/dashboard")
@login_required
def dashboard():
    posts = db.query_all(
        "SELECT id, title, content, created_at FROM posts WHERE user_id=%s ORDER BY created_at DESC",
        (session["user_id"],)
    )
    return render_template("dashboard.html", posts=posts)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Título y contenido son obligatorios.", "danger")
            return redirect(url_for("add_post"))

        db.execute(
            "INSERT INTO posts (user_id, title, content) VALUES (%s, %s, %s)",
            (session["user_id"], title, content)
        )
        flash("Post publicado.", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_post.html")


@app.post("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    # Seguridad: solo borra si el post es del usuario logueado
    post = db.query_one("SELECT id FROM posts WHERE id=%s AND user_id=%s", (post_id, session["user_id"]))
    if not post:
        abort(404)

    db.execute("DELETE FROM posts WHERE id=%s AND user_id=%s", (post_id, session["user_id"]))
    flash("Post eliminado.", "info")
    return redirect(url_for("dashboard"))