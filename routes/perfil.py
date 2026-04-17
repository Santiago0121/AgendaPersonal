from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.tenant import Tenant
from routes.admin import requiere_login

perfil_bp = Blueprint("perfil", __name__)

@perfil_bp.route("/", methods=["GET", "POST"])
@requiere_login
def index():
    tenant_id = session.get("tenant_id")

    if request.method == "POST":
        datos = {
            "nombre":      request.form["nombre"],
            "telefono":    request.form.get("telefono", ""),
            "descripcion": request.form.get("descripcion", ""),
        }
        try:
            Tenant.actualizar_perfil(tenant_id, datos)
            flash("Perfil actualizado correctamente.", "success")
            return redirect(url_for("perfil.index"))
        except Exception as e:
            flash(f"Error al actualizar perfil: {str(e)}", "error")

    tenant = Tenant.obtener(tenant_id)
    return render_template("perfil.html", tenant=tenant)