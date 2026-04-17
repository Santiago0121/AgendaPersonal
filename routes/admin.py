from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from config import supabase_admin
from models.tenant import Tenant
from models.usuario import Usuario
from functools import wraps

admin_bp = Blueprint("admin", __name__)

# Decorador para proteger rutas de admin
def requiere_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        if session.get("rol") != "admin":
            flash("No tienes permisos para acceder aquí.", "error")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated

# Decorador general para cualquier usuario logueado
def requiere_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@requiere_admin
def panel():
    tenants = Tenant.listar()
    return render_template("admin/panel.html", tenants=tenants)


@admin_bp.route("/tenants/crear", methods=["GET", "POST"])
@requiere_admin
def crear_tenant():
    if request.method == "POST":
        nombre   = request.form["nombre"]
        email    = request.form["email"]
        plan     = request.form.get("plan", "free")
        password = request.form["password"]
        nombre_usuario = request.form["nombre_usuario"]

        try:
            # 1. Crear tenant
            tenant = Tenant.crear(nombre, email, plan)

            # 2. Crear usuario en Supabase Auth
            auth_res = supabase_admin.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True
            })

            # 3. Vincular usuario con tenant
            Usuario.crear(
                auth_user_id=str(auth_res.user.id),
                tenant_id=tenant["id"],
                nombre=nombre_usuario,
                rol="usuario"
            )

            flash(f"Tenant '{nombre}' creado correctamente.", "success")
            return redirect(url_for("admin.panel"))

        except Exception as e:
            flash(f"Error al crear tenant: {str(e)}", "error")

    return render_template("admin/crear_tenant.html")


@admin_bp.route("/tenants/eliminar/<tenant_id>", methods=["POST"])
@requiere_admin
def eliminar_tenant(tenant_id):
    Tenant.eliminar(tenant_id)
    flash("Tenant eliminado.", "success")
    return redirect(url_for("admin.panel"))