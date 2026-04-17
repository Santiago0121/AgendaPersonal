from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.evento import Evento
from models.transaccion import Transaccion
from models.tenant import Tenant
from routes.admin import requiere_login
from guitarutils import dias_para_evento, formatear_fecha, formatear_moneda
from datetime import date

eventos_bp = Blueprint("eventos", __name__)

def get_modelo():
    return Evento(session.get("tenant_id"))

@eventos_bp.route("/")
@requiere_login
def index():
    tipo = request.args.get("tipo", "")
    modelo = get_modelo()
    eventos = modelo.listar(tipo if tipo else None)
    for e in eventos:
        e["dias_restantes"] = dias_para_evento(e["fecha"])
        e["fecha_bonita"]   = formatear_fecha(e["fecha"])
        e["valor_fmt"]      = formatear_moneda(e.get("valor") or 0)
    return render_template("eventos/index.html", eventos=eventos, tipo_activo=tipo)

@eventos_bp.route("/crear", methods=["GET", "POST"])
@requiere_login
def crear():
    if request.method == "POST":
        datos = {
            "titulo":               request.form["titulo"],
            "tipo":                 request.form["tipo"],
            "fecha":                request.form["fecha"],
            "hora":                 request.form["hora"],
            "lugar":                request.form.get("lugar", ""),
            "descripcion":          request.form.get("descripcion", ""),
            "valor":                float(request.form.get("valor") or 0),
            "contratante_nombre":   request.form.get("contratante_nombre", ""),
            "contratante_telefono": request.form.get("contratante_telefono", ""),
        }
        try:
            get_modelo().crear(datos)
            flash("Evento creado correctamente.", "success")
            return redirect(url_for("eventos.index"))
        except Exception as e:
            flash(f"Error al crear evento: {str(e)}", "error")
    return render_template("eventos/form.html", evento=None, accion="Crear")

@eventos_bp.route("/editar/<evento_id>", methods=["GET", "POST"])
@requiere_login
def editar(evento_id):
    modelo = get_modelo()
    if request.method == "POST":
        datos = {
            "titulo":               request.form["titulo"],
            "tipo":                 request.form["tipo"],
            "fecha":                request.form["fecha"],
            "hora":                 request.form["hora"],
            "lugar":                request.form.get("lugar", ""),
            "descripcion":          request.form.get("descripcion", ""),
            "valor":                float(request.form.get("valor") or 0),
            "contratante_nombre":   request.form.get("contratante_nombre", ""),
            "contratante_telefono": request.form.get("contratante_telefono", ""),
        }
        try:
            modelo.actualizar(evento_id, datos)
            flash("Evento actualizado correctamente.", "success")
            return redirect(url_for("eventos.index"))
        except Exception as e:
            flash(f"Error al actualizar evento: {str(e)}", "error")
    evento = modelo.obtener(evento_id)
    return render_template("eventos/form.html", evento=evento, accion="Editar")

@eventos_bp.route("/reporte/<evento_id>")
@requiere_login
def reporte(evento_id):
    evento = get_modelo().obtener(evento_id)
    tenant = Tenant.obtener(session.get("tenant_id"))
    evento["fecha_bonita"] = formatear_fecha(evento["fecha"])
    evento["valor_fmt"]    = formatear_moneda(evento.get("valor") or 0)
    return render_template("eventos/reporte.html", evento=evento, tenant=tenant)

@eventos_bp.route("/pagar/<evento_id>", methods=["POST"])
@requiere_login
def marcar_pagado(evento_id):
    modelo = get_modelo()
    try:
        evento = modelo.obtener(evento_id)
        if evento.get("pagado"):
            flash("Este evento ya fue marcado como pagado.", "error")
            return redirect(url_for("eventos.index"))
        if not evento.get("valor") or evento["valor"] <= 0:
            flash("El evento no tiene un valor registrado.", "error")
            return redirect(url_for("eventos.index"))
        Transaccion(session.get("tenant_id")).crear({
            "tipo":        "ingreso",
            "monto":       evento["valor"],
            "descripcion": f"Pago por: {evento['titulo']}",
            "fecha":       date.today().isoformat(),
            "evento_id":   evento_id,
        })
        modelo.actualizar(evento_id, {"pagado": True})
        flash(f"Pago de {formatear_moneda(evento['valor'])} registrado correctamente.", "success")
    except Exception as e:
        flash(f"Error al registrar pago: {str(e)}", "error")
    return redirect(url_for("eventos.index"))

@eventos_bp.route("/eliminar/<evento_id>", methods=["POST"])
@requiere_login
def eliminar(evento_id):
    try:
        get_modelo().eliminar(evento_id)
        flash("Evento eliminado correctamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar: {str(e)}", "error")
    return redirect(url_for("eventos.index"))