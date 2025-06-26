from flask import Blueprint, render_template, request, Response, url_for, redirect, flash # redirect añadido
from flask_login import login_required, current_user # current_user es buena práctica tenerlo
from app.models.cylinder import Cylinder
from app.models.historial import HistorialMovimiento # NUEVA IMPORTACIÓN
from app.forms import DateRangeReportForm # NUEVA IMPORTACIÓN
from app import db
from datetime import datetime, time # time añadido
from app.models.user import User
import io
import csv

bp = Blueprint('reports', __name__)

@bp.route('/')
@login_required
def index():
    return render_template('reports/index.html', title='Reportes')

# ... (Rutas existentes para creaciones, recepciones, entregas y sus CSV SIN CAMBIOS) ...
# (Asegúrese de mantener las versiones de esas rutas que ya tiene y que funcionan)

@bp.route('/creations', methods=['GET', 'POST'])
@login_required
def cylinder_creations_report():
    form = DateRangeReportForm(request.form)
    query = Cylinder.query
    fecha_inicio_data = None
    fecha_fin_data = None

    if request.method == 'POST' and form.clear_filter.data:
        return redirect(url_for('reports.cylinder_creations_report'))

    if form.validate_on_submit() and form.submit_filter.data:
        fecha_inicio_data = form.fecha_inicio.data
        fecha_fin_data = form.fecha_fin.data
    elif request.method == 'GET':
        fecha_inicio_str = request.args.get('fecha_inicio')
        fecha_fin_str = request.args.get('fecha_fin')
        try:
            if fecha_inicio_str: fecha_inicio_data = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            if fecha_fin_str: fecha_fin_data = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            form.fecha_inicio.data = fecha_inicio_data # To display in the form
            form.fecha_fin.data = fecha_fin_data     # To display in the form
        except ValueError:
            flash('Invalid date format in URL. Use YYYY-MM-DD.', 'warning')
    
    if fecha_inicio_data:
        query = query.filter(Cylinder.creation_date >= datetime.combine(fecha_inicio_data, time.min))
    if fecha_fin_data:
        query = query.filter(Cylinder.creation_date <= datetime.combine(fecha_fin_data, time.max))
            
    page = request.args.get('page', 1, type=int)
    creations_pagination = query.order_by(Cylinder.creation_date.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    
    pagination_params = {'page': creations_pagination.next_num}
    if fecha_inicio_data: pagination_params['fecha_inicio'] = fecha_inicio_data.strftime('%Y-%m-%d')
    if fecha_fin_data: pagination_params['fecha_fin'] = fecha_fin_data.strftime('%Y-%m-%d')
    next_url = url_for('reports.cylinder_creations_report', **pagination_params) if creations_pagination.has_next else None
    
    pagination_params['page'] = creations_pagination.prev_num
    prev_url = url_for('reports.cylinder_creations_report', **pagination_params) if creations_pagination.has_prev else None

    return render_template('reports/creations_report.html', 
                           title='Cylinder Creation Report',
                           form=form,
                           cylinders=creations_pagination.items,
                           pagination=creations_pagination,
                           next_url=next_url, prev_url=prev_url,
                           current_fecha_inicio=fecha_inicio_data.strftime('%Y-%m-%d') if fecha_inicio_data else None,
                           current_fecha_fin=fecha_fin_data.strftime('%Y-%m-%d') if fecha_fin_data else None)

@bp.route('/creations/export_csv')
@login_required
def export_creations_csv():
    query = Cylinder.query
    fecha_inicio_str = request.args.get('fecha_inicio', None)
    fecha_fin_str = request.args.get('fecha_fin', None)

    if fecha_inicio_str:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            query = query.filter(Cylinder.creation_date >= datetime.combine(fecha_inicio_obj, time.min))
        except ValueError: pass
    if fecha_fin_str:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            query = query.filter(Cylinder.creation_date <= datetime.combine(fecha_fin_obj, time.max))
        except ValueError: pass

    cylinders = query.order_by(Cylinder.creation_date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    headers = ['Cylinder ID', 'Status', 'Creation Date', 'Delivery Date', 'Reception Date']
    writer.writerow(headers)
    for cylinder in cylinders:
        row = [
            cylinder.cylinder_id_tag,
            cylinder.status,
            cylinder.creation_date.strftime('%Y-%m-%d %H:%M:%S UTC') if cylinder.creation_date else 'N/A',
            cylinder.delivery_date.strftime('%Y-%m-%d %H:%M:%S UTC') if cylinder.delivery_date else 'N/A',
            cylinder.reception_date.strftime('%Y-%m-%d %H:%M:%S UTC') if cylinder.reception_date else 'N/A'
        ]
        writer.writerow(row)
    csv_output = output.getvalue()
    output.close()
    return Response(
        csv_output,
        mimetype="text/csv",
        headers={"Content-Disposition":"attachment;filename=creations_report.csv"})

@bp.route('/receptions', methods=['GET', 'POST'])
@login_required
def cylinder_receptions_report():
    form = DateRangeReportForm(request.form)
    query = Cylinder.query.filter(Cylinder.reception_date.isnot(None))
    fecha_inicio_data = None
    fecha_fin_data = None

    if request.method == 'POST' and form.clear_filter.data:
        return redirect(url_for('reports.cylinder_receptions_report'))

    if form.validate_on_submit() and form.submit_filter.data:
        fecha_inicio_data = form.fecha_inicio.data
        fecha_fin_data = form.fecha_fin.data
    elif request.method == 'GET':
        fecha_inicio_str = request.args.get('fecha_inicio')
        fecha_fin_str = request.args.get('fecha_fin')
        try:
            if fecha_inicio_str: fecha_inicio_data = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            if fecha_fin_str: fecha_fin_data = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            form.fecha_inicio.data = fecha_inicio_data
            form.fecha_fin.data = fecha_fin_data
        except ValueError:
            flash('Formato de fecha inválido en URL. Use YYYY-MM-DD.', 'warning')
    
    if fecha_inicio_data:
        query = query.filter(Cylinder.reception_date >= datetime.combine(fecha_inicio_data, time.min))
    if fecha_fin_data:
        query = query.filter(Cylinder.reception_date <= datetime.combine(fecha_fin_data, time.max))
            
    page = request.args.get('page', 1, type=int)
    receptions_pagination = query.order_by(Cylinder.reception_date.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    
    pagination_params = {'page': receptions_pagination.next_num}
    if fecha_inicio_data: pagination_params['fecha_inicio'] = fecha_inicio_data.strftime('%Y-%m-%d')
    if fecha_fin_data: pagination_params['fecha_fin'] = fecha_fin_data.strftime('%Y-%m-%d')
    next_url = url_for('reports.cylinder_receptions_report', **pagination_params) if receptions_pagination.has_next else None
    
    pagination_params['page'] = receptions_pagination.prev_num
    prev_url = url_for('reports.cylinder_receptions_report', **pagination_params) if receptions_pagination.has_prev else None

    return render_template('reports/receptions_report.html', 
                           title='Reporte de Recepción de Botellones',
                           form=form,
                           cylinders=receptions_pagination.items,
                           pagination=receptions_pagination,
                           next_url=next_url, prev_url=prev_url,
                           current_fecha_inicio=fecha_inicio_data.strftime('%Y-%m-%d') if fecha_inicio_data else None,
                           current_fecha_fin=fecha_fin_data.strftime('%Y-%m-%d') if fecha_fin_data else None)

@bp.route('/receptions/export_csv')
@login_required
def export_receptions_csv():
    query = Cylinder.query.filter(Cylinder.reception_date.isnot(None))
    fecha_inicio_str = request.args.get('fecha_inicio', None)
    fecha_fin_str = request.args.get('fecha_fin', None)

    if fecha_inicio_str:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            query = query.filter(Cylinder.reception_date >= datetime.combine(fecha_inicio_obj, time.min))
        except ValueError: pass
    if fecha_fin_str:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            query = query.filter(Cylinder.reception_date <= datetime.combine(fecha_fin_obj, time.max))
        except ValueError: pass

    cylinders = query.order_by(Cylinder.reception_date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    headers = ['ID Botellón', 'Estado', 'Fecha Recepción', 'Fecha Creación', 'Últ. Entrega']
    writer.writerow(headers)
    for cylinder in cylinders:
        row = [
            cylinder.cylinder_id_tag,
            cylinder.status,
            cylinder.reception_date.strftime('%Y-%m-%d %H:%M:%S UTC') if cylinder.reception_date else 'N/A',
            cylinder.creation_date.strftime('%Y-%m-%d %H:%M:%S UTC') if cylinder.creation_date else 'N/A',
            cylinder.delivery_date.strftime('%Y-%m-%d %H:%M:%S UTC') if cylinder.delivery_date else 'N/A'
        ]
        writer.writerow(row)
    csv_output = output.getvalue()
    output.close()
    return Response(
        csv_output,
        mimetype="text/csv",
        headers={"Content-Disposition":"attachment;filename=reporte_recepciones.csv"})

@bp.route('/deliveries', methods=['GET', 'POST'])
@login_required
def cylinder_deliveries_report():
    form = DateRangeReportForm(request.form)
    query = Cylinder.query.filter(Cylinder.delivery_date.isnot(None))
    fecha_inicio_data = None
    fecha_fin_data = None

    if request.method == 'POST' and form.clear_filter.data:
        return redirect(url_for('reports.cylinder_deliveries_report'))

    if form.validate_on_submit() and form.submit_filter.data:
        fecha_inicio_data = form.fecha_inicio.data
        fecha_fin_data = form.fecha_fin.data
    elif request.method == 'GET':
        fecha_inicio_str = request.args.get('fecha_inicio')
        fecha_fin_str = request.args.get('fecha_fin')
        try:
            if fecha_inicio_str: fecha_inicio_data = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            if fecha_fin_str: fecha_fin_data = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            form.fecha_inicio.data = fecha_inicio_data
            form.fecha_fin.data = fecha_fin_data
        except ValueError:
            flash('Formato de fecha inválido en URL. Use YYYY-MM-DD.', 'warning')

    if fecha_inicio_data:
        query = query.filter(Cylinder.delivery_date >= datetime.combine(fecha_inicio_data, time.min))
    if fecha_fin_data:
        query = query.filter(Cylinder.delivery_date <= datetime.combine(fecha_fin_data, time.max))
            
    page = request.args.get('page', 1, type=int)
    deliveries_pagination = query.order_by(Cylinder.delivery_date.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    
    pagination_params = {'page': deliveries_pagination.next_num}
    if fecha_inicio_data: pagination_params['fecha_inicio'] = fecha_inicio_data.strftime('%Y-%m-%d')
    if fecha_fin_data: pagination_params['fecha_fin'] = fecha_fin_data.strftime('%Y-%m-%d')
    next_url = url_for('reports.cylinder_deliveries_report', **pagination_params) if deliveries_pagination.has_next else None
    
    pagination_params['page'] = deliveries_pagination.prev_num
    prev_url = url_for('reports.cylinder_deliveries_report', **pagination_params) if deliveries_pagination.has_prev else None

    return render_template('reports/deliveries_report.html', 
                           title='Reporte de Entrega de Botellones',
                           form=form,
                           cylinders=deliveries_pagination.items,
                           pagination=deliveries_pagination,
                           next_url=next_url, prev_url=prev_url,
                           current_fecha_inicio=fecha_inicio_data.strftime('%Y-%m-%d') if fecha_inicio_data else None,
                           current_fecha_fin=fecha_fin_data.strftime('%Y-%m-%d') if fecha_fin_data else None)

@bp.route('/deliveries/export_csv')
@login_required
def export_deliveries_csv():
    query = Cylinder.query.filter(Cylinder.delivery_date.isnot(None))
    fecha_inicio_str = request.args.get('fecha_inicio', None)
    fecha_fin_str = request.args.get('fecha_fin', None)

    if fecha_inicio_str:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            query = query.filter(Cylinder.delivery_date >= datetime.combine(fecha_inicio_obj, time.min))
        except ValueError: pass
    if fecha_fin_str:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            query = query.filter(Cylinder.delivery_date <= datetime.combine(fecha_fin_obj, time.max))
        except ValueError: pass

    cylinders = query.order_by(Cylinder.delivery_date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    headers = ['ID Botellón', 'Estado', 'Fecha Entrega', 'Fecha Creación', 'Últ. Recepción']
    writer.writerow(headers)
    for cylinder in cylinders:
        row = [
            cylinder.cylinder_id_tag,
            cylinder.status,
            cylinder.delivery_date.strftime('%Y-%m-%d %H:%M:%S UTC') if cylinder.delivery_date else 'N/A',
            cylinder.creation_date.strftime('%Y-%m-%d %H:%M:%S UTC') if cylinder.creation_date else 'N/A',
            cylinder.reception_date.strftime('%Y-%m-%d %H:%M:%S UTC') if cylinder.reception_date else 'N/A'
        ]
        writer.writerow(row)
    csv_output = output.getvalue()
    output.close()
    return Response(
        csv_output,
        mimetype="text/csv",
        headers={"Content-Disposition":"attachment;filename=reporte_entregas.csv"})

@bp.route('/historical_movements', methods=['GET', 'POST'])
@login_required
def historical_movements_report():
    form = DateRangeReportForm(request.form)
    query = HistorialMovimiento.query.join(Cylinder).join(User)
    fecha_inicio_str = request.values.get('fecha_inicio', None)
    fecha_fin_str = request.values.get('fecha_fin', None)

    if form.clear_filter.data:
        return redirect(url_for('reports.historical_movements_report'))

    if form.validate_on_submit() and form.submit_filter.data:
        if form.fecha_inicio.data:
            query = query.filter(HistorialMovimiento.fecha_movimiento >= form.fecha_inicio.data)
        if form.fecha_fin.data:
            fecha_fin_con_hora = datetime.combine(form.fecha_fin.data, time.max)
            query = query.filter(HistorialMovimiento.fecha_movimiento <= fecha_fin_con_hora)
    elif fecha_inicio_str or fecha_fin_str:
        try:
            if fecha_inicio_str:
                fecha_inicio_obj = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                form.fecha_inicio.data = fecha_inicio_obj
                query = query.filter(HistorialMovimiento.fecha_movimiento >= fecha_inicio_obj)
        except ValueError:
            flash('Formato de Fecha de Inicio inválido. Use YYYY-MM-DD.', 'danger')
        try:
            if fecha_fin_str:
                fecha_fin_obj = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                form.fecha_fin.data = fecha_fin_obj
                fecha_fin_con_hora = datetime.combine(fecha_fin_obj, time.max)
                query = query.filter(HistorialMovimiento.fecha_movimiento <= fecha_fin_con_hora)
        except ValueError:
            flash('Formato de Fecha de Fin inválido. Use YYYY-MM-DD.', 'danger')

    page = request.args.get('page', 1, type=int)
    movements_pagination = query.order_by(HistorialMovimiento.fecha_movimiento.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    pagination_params = {'page': movements_pagination.next_num}
    if form.fecha_inicio.data: pagination_params['fecha_inicio'] = form.fecha_inicio.data.strftime('%Y-%m-%d')
    if form.fecha_fin.data: pagination_params['fecha_fin'] = form.fecha_fin.data.strftime('%Y-%m-%d')
    next_url = url_for('reports.historical_movements_report', **pagination_params) if movements_pagination.has_next else None
    pagination_params['page'] = movements_pagination.prev_num
    prev_url = url_for('reports.historical_movements_report', **pagination_params) if movements_pagination.has_prev else None

    return render_template('reports/historical_movements_report.html',
                           title='Reporte Histórico de Movimientos',
                           form=form,
                           movimientos=movements_pagination.items,
                           pagination=movements_pagination,
                           next_url=next_url,
                           prev_url=prev_url,
                           current_fecha_inicio=form.fecha_inicio.data.strftime('%Y-%m-%d') if form.fecha_inicio.data else None,
                           current_fecha_fin=form.fecha_fin.data.strftime('%Y-%m-%d') if form.fecha_fin.data else None
                           )

@bp.route('/historical_movements/export_csv')
@login_required
def export_historical_movements_csv():
    query = HistorialMovimiento.query.join(Cylinder).join(User)
    fecha_inicio_str = request.args.get('fecha_inicio', None)
    fecha_fin_str = request.args.get('fecha_fin', None)
    if fecha_inicio_str:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            query = query.filter(HistorialMovimiento.fecha_movimiento >= fecha_inicio_obj)
        except ValueError: pass
    if fecha_fin_str:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            fecha_fin_con_hora = datetime.combine(fecha_fin_obj, time.max)
            query = query.filter(HistorialMovimiento.fecha_movimiento <= fecha_fin_con_hora)
        except ValueError: pass
    movimientos = query.order_by(HistorialMovimiento.fecha_movimiento.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    headers = [
        'ID Movimiento', 'ID Botellón', 'Tipo Movimiento', 'Fecha Movimiento', 
        'Usuario Registra', 'Nombre Contraparte', 'Nota'
    ]
    writer.writerow(headers)
    for movimiento in movimientos:
        row = [
            movimiento.id,
            movimiento.cilindro.cylinder_id_tag if movimiento.cilindro else 'N/A',
            movimiento.tipo_movimiento,
            movimiento.fecha_movimiento.strftime('%Y-%m-%d %H:%M:%S UTC') if movimiento.fecha_movimiento else 'N/A',
            movimiento.usuario.username if movimiento.usuario else 'N/A',
            movimiento.nombre_contraparte or '',
            movimiento.nota or ''
        ]
        writer.writerow(row)
    csv_output = output.getvalue()
    output.close()
    return Response(
        csv_output,
        mimetype="text/csv",
        headers={"Content-Disposition":"attachment;filename=reporte_historico_movimientos.csv"})

