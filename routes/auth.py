from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from config import supabase
from models.usuario import Usuario

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form["email"]
        password = request.form["password"]
        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            auth_user = res.user
            usuario = Usuario.obtener_por_auth_id(str(auth_user.id))

            if not usuario:
                flash("Tu cuenta no está asociada a ningún tenant. Contacta al administrador.", "error")
                return redirect(url_for("auth.login"))

            # Guardar en sesión Flask
            session["user_id"]   = str(auth_user.id)
            session["tenant_id"] = usuario["tenant_id"]
            session["nombre"]    = usuario["nombre"]
            session["rol"]       = usuario["rol"]
            session["token"]     = res.session.access_token

            return redirect(url_for("dashboard"))

        except Exception as e:
            flash("Email o contraseña incorrectos.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    supabase.auth.sign_out()
    session.clear()
    return redirect(url_for("auth.login"))