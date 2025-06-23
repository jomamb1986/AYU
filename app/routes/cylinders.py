# <!-- este es el codigo COMPLETO para app/routes/cylinders.py PARTE 1 -->
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.cylinder import Cylinder
from app.models.user import User
from app.models.historial import HistorialMovimiento
from app.forms import CreateCylinderForm, UpdateCylinderStatusForm, BatchProcessForm, EditCylinderForm # Todos los forms
from datetime import datetime # datetime para fechas

bp = Blueprint('cylinders', __name__)

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    query_term = request.args.get('q', None, type=str)
    base_query = Cylinder.query
    if query_term:
        search_filter = f"%{query_term}%"
        base_query = base_query.filter(Cylinder.cylinder_id_tag.ilike(search_filter))
    cylinders_pagination = base_query.order_by(Cylinder.creation_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    next_url_params = {'page': cylinders_pagination.next_num}
    if query_term:
        next_url_params['q'] = query_term
    next_url = url_for('cylinders.index', **next_url_params) if cylinders_pagination.has_next else None
    prev_url_params = {'page': cylinders_pagination.prev_num}
    if query_term:
        prev_url_params['q'] = query_term
    prev_url = url_for('cylinders.index', **prev_url_params) if cylinders_pagination.has_prev else None
    return render_template('cylinders/index.html',
                           title='Botellones de Oxígeno',
                           cylinders=cylinders_pagination.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           pagination=cylinders_pagination,
                           current_query=query_term)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_cylinder():
    form = CreateCylinderForm()
    if form.validate_on_submit():
        cylinder = Cylinder(
            cylinder_id_tag=form.cylinder_id_tag.data,
            status='available',
            marca=form.marca.data,
            color=form.color.data,
            numero_serie=form.numero_serie.data
        )
        db.session.add(cylinder)
        db.session.commit()

        historial_creacion = HistorialMovimiento(
            cylinder_id=cylinder.id,
            user_id=current_user.id,
            tipo_movimiento="creacion",
            fecha_movimiento=cylinder.creation_date,
            nombre_contraparte=None,
            nota=f"Botellón registrado. Marca: {cylinder.marca or 'N/A'}, Color: {cylinder.color or 'N/A'}, Serie: {cylinder.numero_serie or 'N/A'}."
        )
        db.session.add(historial_creacion)
        db.session.commit()

        flash(f'Botellón {cylinder.cylinder_id_tag} ha sido creado (con detalles adicionales) y registrado en el historial.', 'success')
        return redirect(url_for('cylinders.index'))
    return render_template('cylinders/create_cylinder.html', title='Crear Nuevo Botellón', form=form)

@bp.route('/<int:cylinder_id>')
@login_required
def view_cylinder(cylinder_id):
    cylinder = Cylinder.query.get_or_404(cylinder_id)
    movimientos = cylinder.historial_movimientos.all()
    return render_template('cylinders/view_cylinder.html',
                           title=f'Botellón {cylinder.cylinder_id_tag}',
                           cylinder=cylinder,
                           movimientos=movimientos)

@bp.route('/<int:cylinder_id>/update_status', methods=['GET', 'POST'])
@login_required
def update_cylinder_status(cylinder_id):
    cylinder = Cylinder.query.get_or_404(cylinder_id)
    form = UpdateCylinderStatusForm(obj=cylinder) 
    if form.validate_on_submit():
        new_status_from_form = form.status.data
        cylinder.status = new_status_from_form
        tipo_movimiento_historial = None
        fecha_para_historial = datetime.utcnow()
        if new_status_from_form == 'delivered':
            cylinder.delivery_date = fecha_para_historial
            cylinder.reception_date = None
            tipo_movimiento_historial = "entrega"
        elif new_status_from_form == 'received':
            cylinder.reception_date = fecha_para_historial
            tipo_movimiento_historial = "recepcion"
        
        historial_entry = HistorialMovimiento(
            cylinder_id=cylinder.id,
            user_id=current_user.id,
            tipo_movimiento=tipo_movimiento_historial,
            fecha_movimiento=fecha_para_historial,
            nombre_contraparte=form.nombre_contraparte.data,
            nota=form.nota_movimiento.data
        )
        db.session.add(historial_entry)
        db.session.commit()
        flash(f'El estado del botellón {cylinder.cylinder_id_tag} ha sido actualizado a "{new_status_from_form}" y el movimiento registrado en el historial.', 'success')
        return redirect(url_for('cylinders.view_cylinder', cylinder_id=cylinder.id))
    return render_template('cylinders/update_cylinder_status.html', 
                           title=f'Registrar Movimiento para {cylinder.cylinder_id_tag}', 
                           form=form, cylinder=cylinder)

@bp.route('/<int:cylinder_id>/delete', methods=['POST'])
@login_required
def delete_cylinder(cylinder_id):
    if current_user.role != 'admin':
        abort(403)
    cylinder = Cylinder.query.get_or_404(cylinder_id)
    db.session.delete(cylinder)
    db.session.commit()
    flash(f'Botellón {cylinder.cylinder_id_tag} ha sido eliminado.', 'success')
    return redirect(url_for('cylinders.index'))


@bp.route('/<int:cylinder_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_cylinder(cylinder_id):
    cylinder = Cylinder.query.get_or_404(cylinder_id)
    form = EditCylinderForm(obj=cylinder)

    if request.method == 'POST' and form.validate_on_submit():
        old_values = {
            'marca': cylinder.marca,
            'color': cylinder.color,
            'numero_serie': cylinder.numero_serie,
            'status': cylinder.status
        }
        cylinder.marca = form.marca.data
        cylinder.color = form.color.data
        cylinder.numero_serie = form.numero_serie.data
        new_status_from_form = form.status.data
        status_changed = cylinder.status != new_status_from_form
        cylinder.status = new_status_from_form

        if new_status_from_form == 'available' and status_changed:
            cylinder.delivery_date = None
            cylinder.reception_date = None
        
        changes_summary = []
        if old_values['marca'] != cylinder.marca: changes_summary.append(f"Marca: '{old_values['marca'] or ''}' -> '{cylinder.marca or ''}'")
        if old_values['color'] != cylinder.color: changes_summary.append(f"Color: '{old_values['color'] or ''}' -> '{cylinder.color or ''}'")
        if old_values['numero_serie'] != cylinder.numero_serie: changes_summary.append(f"N° Serie: '{old_values['numero_serie'] or ''}' -> '{cylinder.numero_serie or ''}'")
        if status_changed: changes_summary.append(f"Estado: '{old_values['status']}' -> '{cylinder.status}'")
        
        nota_historial = "Actualización de datos del botellón."
        if changes_summary: nota_historial += " Cambios: " + "; ".join(changes_summary) + "."
        else: nota_historial += " Se guardaron los datos (sin cambios detectables en campos principales)."
        if form.nota_edicion.data: nota_historial += f" Nota adicional de edición: {form.nota_edicion.data}"

        historial_edicion = HistorialMovimiento(
            cylinder_id=cylinder.id, user_id=current_user.id,
            tipo_movimiento="actualizacion_info", fecha_movimiento=datetime.utcnow(),
            nota=nota_historial 
        )
        db.session.add(historial_edicion)
        
        try:
            db.session.commit()
            flash('Los datos del botellón han sido actualizados exitosamente y la edición registrada en el historial.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el botellón: {str(e)}', 'danger')
        return redirect(url_for('cylinders.view_cylinder', cylinder_id=cylinder.id))
    
    return render_template('cylinders/edit_cylinder.html', 
                           title=f'Editar Botellón: {cylinder.cylinder_id_tag}', 
                           form=form, 
                           cylinder_id_tag_display=cylinder.cylinder_id_tag)

@bp.route('/process-batch', methods=['POST'])
@login_required
def process_batch_action_page():
    selected_ids = request.form.getlist('selected_cylinder_ids')
    action_type = request.form.get('batch_action_type')
    if not selected_ids:
        flash('No se seleccionó ningún botellón para procesar.', 'warning')
        return redirect(url_for('cylinders.index'))
    if action_type not in ['deliver', 'receive']:
        flash('Tipo de acción en lote no válida.', 'danger')
        return redirect(url_for('cylinders.index'))
    ids_csv = ",".join(selected_ids)
    form = BatchProcessForm()
    form.selected_ids_csv.data = ids_csv
    form.action_type.data = action_type
    cylinders_to_process = Cylinder.query.filter(Cylinder.id.in_(selected_ids)).all()
    if action_type == 'deliver':
        page_title = "Registrar Entrega de Lote de Botellones"
        submit_button_label = "Confirmar Entrega del Lote"
        contraparte_label = "Nombre del Destinatario del Lote"
    else:
        page_title = "Registrar Recepción de Lote de Botellones"
        submit_button_label = "Confirmar Recepción del Lote"
        contraparte_label = "Nombre del Remitente del Lote"
    if hasattr(form, 'submit') and hasattr(form.submit, 'label'): form.submit.label.text = submit_button_label
    if hasattr(form, 'nombre_contraparte') and hasattr(form.nombre_contraparte, 'label'): form.nombre_contraparte.label.text = contraparte_label
    return render_template('cylinders/process_batch_form.html',
                           title=page_title, form=form,
                           cylinders_selected=cylinders_to_process,
                           action_type_display=action_type.replace('deliver', 'Entrega').replace('receive', 'Recepción'))

@bp.route('/execute-batch', methods=['POST'])
@login_required
def execute_batch_action():
    form = BatchProcessForm()
    if form.validate_on_submit():
        ids_to_process_str = form.selected_ids_csv.data
        action = form.action_type.data
        nombre_contraparte = form.nombre_contraparte.data
        nota = form.nota_movimiento.data
        selected_ids = ids_to_process_str.split(',')
        if not selected_ids or selected_ids == ['']:
            flash('Error: No se recibieron IDs de botellones para procesar.', 'danger')
            return redirect(url_for('cylinders.index'))
        updated_count = 0
        error_ids = []
        for cylinder_id_str in selected_ids:
            if not cylinder_id_str.strip(): continue
            try:
                cylinder_id = int(cylinder_id_str)
                cylinder = Cylinder.query.get(cylinder_id)
                if not cylinder:
                    flash(f'Advertencia: No se encontró ID {cylinder_id_str}. Se omitió.', 'warning'); error_ids.append(cylinder_id_str); continue
                current_time = datetime.utcnow(); tipo_mov_hist = None
                if action == 'deliver':
                    if cylinder.status in ['available', 'received', 'maintenance']:
                        cylinder.status = 'delivered'; cylinder.delivery_date = current_time; cylinder.reception_date = None; tipo_mov_hist = 'entrega'
                    else:
                        flash(f'Botellón {cylinder.cylinder_id_tag} (estado: {cylinder.status}) no apto para entrega. Se omitió.', 'warning'); error_ids.append(cylinder_id_str); continue
                elif action == 'receive':
                    if cylinder.status in ['delivered', 'maintenance']:
                        cylinder.status = 'received'; cylinder.reception_date = current_time; tipo_mov_hist = 'recepcion'
                    else:
                        flash(f'Botellón {cylinder.cylinder_id_tag} (estado: {cylinder.status}) no apto para recepción. Se omitió.', 'warning'); error_ids.append(cylinder_id_str); continue
                if tipo_mov_hist:
                    db.session.add(HistorialMovimiento(cylinder_id=cylinder.id, user_id=current_user.id, tipo_movimiento=tipo_mov_hist, fecha_movimiento=current_time, nombre_contraparte=nombre_contraparte, nota=nota))
                    updated_count += 1
            except ValueError:
                flash(f'Advertencia: ID no válido: "{cylinder_id_str}". Se omitió.', 'warning'); error_ids.append(cylinder_id_str); continue
        if updated_count > 0:
            try:
                db.session.commit()
                flash(f'{updated_count} botellón(es) procesados exitosamente.', 'success')
            except Exception as e:
                db.session.rollback(); flash(f'Error al guardar: {str(e)}', 'danger')
        elif not error_ids: flash('No se procesó ningún botellón. Verifique selección/estados.', 'info')
        return redirect(url_for('cylinders.index'))
    else:
        ids_csv_from_hidden = request.form.get('selected_ids_csv', ''); action_type_from_hidden = request.form.get('action_type', '')
        selected_ids_list = ids_csv_from_hidden.split(',') if ids_csv_from_hidden else []
        valid_selected_ids_list = [sid for sid in selected_ids_list if sid.strip().isdigit()]
        cylinders_to_process = Cylinder.query.filter(Cylinder.id.in_(valid_selected_ids_list)).all() if valid_selected_ids_list else []
        page_title = "Corrija Errores en Formulario de Lote"; action_type_display_text = action_type_from_hidden.replace('deliver', 'Entrega').replace('receive', 'Recepción')
        if action_type_from_hidden == 'deliver': page_title = "Registrar Entrega de Lote (Error)"
        elif action_type_from_hidden == 'receive': page_title = "Registrar Recepción de Lote (Error)"
        flash('Hubo errores en el formulario. Por favor, corríjalos.', 'danger')
        return render_template('cylinders/process_batch_form.html', title=page_title, form=form, cylinders_selected=cylinders_to_process, action_type_display=action_type_display_text)                                                                                     

