from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.cancion import Cancion
from routes.admin import requiere_login
from guitarutils import porcentaje_repertorio_listo

canciones_bp = Blueprint("canciones", __name__)

def get_modelo():
    return Cancion(session.get("tenant_id"))

@canciones_bp.route("/")
@requiere_login
def index():
    estado = request.args.get("estado", "")
    modelo = get_modelo()
    canciones = modelo.listar(estado if estado else None)
    todas    = modelo.listar()
    progreso = porcentaje_repertorio_listo(todas)

    return render_template("canciones/index.html",
                           canciones=canciones,
                           estado_activo=estado,
                           progreso=progreso,
                           total=len(todas))

@canciones_bp.route("/crear", methods=["GET", "POST"])
@requiere_login
def crear():
    if request.method == "POST":
        datos = {
            "titulo":     request.form["titulo"],
            "artista":    request.form.get("artista", ""),
            "tonalidad":  request.form.get("tonalidad", ""),
            "dificultad": int(request.form.get("dificultad", 1)),
            "estado":     request.form.get("estado", "aprendiendo"),
            "notas":      request.form.get("notas", ""),
        }
        try:
            get_modelo().crear(datos)
            flash("Canción agregada al repertorio.", "success")
            return redirect(url_for("canciones.index"))
        except Exception as e:
            flash(f"Error al crear canción: {str(e)}", "error")

    return render_template("canciones/form.html", cancion=None, accion="Agregar")

@canciones_bp.route("/editar/<cancion_id>", methods=["GET", "POST"])
@requiere_login
def editar(cancion_id):
    modelo = get_modelo()

    if request.method == "POST":
        datos = {
            "titulo":     request.form["titulo"],
            "artista":    request.form.get("artista", ""),
            "tonalidad":  request.form.get("tonalidad", ""),
            "dificultad": int(request.form.get("dificultad", 1)),
            "estado":     request.form.get("estado", "aprendiendo"),
            "notas":      request.form.get("notas", ""),
        }
        try:
            modelo.actualizar(cancion_id, datos)
            flash("Canción actualizada correctamente.", "success")
            return redirect(url_for("canciones.index"))
        except Exception as e:
            flash(f"Error al actualizar: {str(e)}", "error")

    cancion = modelo.obtener(cancion_id)
    return render_template("canciones/form.html", cancion=cancion, accion="Editar")

@canciones_bp.route("/eliminar/<cancion_id>", methods=["POST"])
@requiere_login
def eliminar(cancion_id):
    try:
        get_modelo().eliminar(cancion_id)
        flash("Canción eliminada del repertorio.", "success")
    except Exception as e:
        flash(f"Error al eliminar: {str(e)}", "error")
    return redirect(url_for("canciones.index"))