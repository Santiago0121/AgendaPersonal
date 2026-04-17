from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.contacto import Contacto
from routes.admin import requiere_login

contactos_bp = Blueprint("contactos", __name__)

def get_modelo():
    return Contacto(session.get("tenant_id"))

@contactos_bp.route("/")
@requiere_login
def index():
    contactos = get_modelo().listar()
    return render_template("contactos/index.html", contactos=contactos)

@contactos_bp.route("/crear", methods=["GET", "POST"])
@requiere_login
def crear():
    if request.method == "POST":
        datos = {
            "nombre":   request.form["nombre"],
            "rol":      request.form.get("rol", ""),
            "telefono": request.form.get("telefono", ""),
            "email":    request.form.get("email", ""),
            "notas":    request.form.get("notas", ""),
        }
        try:
            get_modelo().crear(datos)
            flash("Contacto agregado correctamente.", "success")
            return redirect(url_for("contactos.index"))
        except Exception as e:
            flash(f"Error al crear contacto: {str(e)}", "error")

    return render_template("contactos/form.html", contacto=None, accion="Agregar")

@contactos_bp.route("/editar/<contacto_id>", methods=["GET", "POST"])
@requiere_login
def editar(contacto_id):
    modelo = get_modelo()

    if request.method == "POST":
        datos = {
            "nombre":   request.form["nombre"],
            "rol":      request.form.get("rol", ""),
            "telefono": request.form.get("telefono", ""),
            "email":    request.form.get("email", ""),
            "notas":    request.form.get("notas", ""),
        }
        try:
            modelo.actualizar(contacto_id, datos)
            flash("Contacto actualizado correctamente.", "success")
            return redirect(url_for("contactos.index"))
        except Exception as e:
            flash(f"Error al actualizar: {str(e)}", "error")

    contacto = modelo.obtener(contacto_id)
    return render_template("contactos/form.html", contacto=contacto, accion="Editar")

@contactos_bp.route("/eliminar/<contacto_id>", methods=["POST"])
@requiere_login
def eliminar(contacto_id):
    try:
        get_modelo().eliminar(contacto_id)
        flash("Contacto eliminado correctamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar: {str(e)}", "error")
    return redirect(url_for("contactos.index"))