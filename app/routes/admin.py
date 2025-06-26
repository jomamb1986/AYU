from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.forms import EditUserRoleForm # Make sure this form is created
from app.models.cylinder import Cylinder
from app.models.historial import HistorialMovimiento
from datetime import datetime # Para la fecha del historial

bp = Blueprint('admin', __name__)

# Define a decorator that checks if the current user is an admin
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('index')) # Or wherever non-admins should go
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@admin_required
def index():
    return redirect(url_for('admin.dashboard'))

@bp.route('/dashboard')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html', title='Admin Dashboard')

@bp.route('/users')
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    # Corrected pagination: Flask-SQLAlchemy paginate() returns a Pagination object
    pagination = User.query.paginate(page=page, per_page=10, error_out=False)
    users = pagination.items
    next_url = url_for('admin.manage_users', page=pagination.next_num) if pagination.has_next else None
    prev_url = url_for('admin.manage_users', page=pagination.prev_num) if pagination.has_prev else None
    return render_template('admin/manage_users.html', users=users, title='Manage Users', next_url=next_url, prev_url=prev_url, pagination=pagination)


@bp.route('/user/<int:user_id>/edit_role', methods=['GET', 'POST'])
@admin_required
def edit_user_role(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id: # Admin cannot change their own role through this form
        flash('Admins cannot change their own role using this form.', 'warning')
        return redirect(url_for('admin.manage_users'))
    form = EditUserRoleForm(obj=user) # Pre-populate form with user's current role
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.commit()
        flash(f"User {user.username}'s role has been updated to {user.role}.", 'success')
        return redirect(url_for('admin.manage_users'))
    return render_template('admin/edit_user_role.html', title='Edit User Role', form=form, user=user)

@bp.route('/cylinders/inactive')
@login_required
def inactive_cylinders_list():
    if not current_user.is_authenticated or current_user.role != 'admin':
        abort(403)
    page = request.args.get('page', 1, type=int)
    cylinders_pagination = Cylinder.query.filter_by(esta_activo=False)\
                                       .order_by(Cylinder.cylinder_id_tag.asc())\
                                       .paginate(page=page, per_page=15, error_out=False)
    next_url = url_for('admin.inactive_cylinders_list', page=cylinders_pagination.next_num) if cylinders_pagination.has_next else None
    prev_url = url_for('admin.inactive_cylinders_list', page=cylinders_pagination.prev_num) if cylinders_pagination.has_prev else None
    return render_template('admin/inactive_cylinders.html',
                           title='Botellones Inactivos',
                           cylinders=cylinders_pagination.items,
                           pagination=cylinders_pagination,
                           next_url=next_url,
                           prev_url=prev_url)    

@bp.route('/cylinder/<int:cylinder_id>/reactivate', methods=['POST'])
@login_required
def reactivate_cylinder(cylinder_id):
    if not current_user.is_authenticated or current_user.role != 'admin':
        abort(403)

    cylinder = Cylinder.query.get_or_404(cylinder_id)

    if cylinder.esta_activo:
        flash(f'El botellón {cylinder.cylinder_id_tag} ya está activo.', 'info')
    else:
        cylinder.esta_activo = True
        cylinder.status = 'available' 
        
        historial_reactivacion = HistorialMovimiento(
            cylinder_id=cylinder.id,
            user_id=current_user.id,
            tipo_movimiento="reactivado",
            fecha_movimiento=datetime.utcnow(),
            nota=f"Botellón {cylinder.cylinder_id_tag} reactivado por {current_user.username}."
        )
        db.session.add(historial_reactivacion)
        
        try:
            db.session.commit()
            flash(f'Botellón {cylinder.cylinder_id_tag} ha sido reactivado y puesto como \"disponible\".', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al reactivar el botellón: {str(e)}', 'danger')
            
    return redirect(url_for('admin.inactive_cylinders_list'))

@bp.route('/user/<int:user_id>/deactivate', methods=['POST'])
@login_required
@admin_required # Asegúrate que este decorador esté definido y funcione
def deactivate_user(user_id):
    user_to_deactivate = User.query.get_or_404(user_id)

    if user_to_deactivate.id == current_user.id:
        flash('No puede desactivar su propia cuenta.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    if not user_to_deactivate.esta_activo:
        flash(f'El usuario {user_to_deactivate.username} ya está desactivado.', 'info')
    else:
        user_to_deactivate.esta_activo = False
        db.session.commit()
        flash(f'El usuario {user_to_deactivate.username} ha sido desactivado.', 'success')
    
    return redirect(url_for('admin.manage_users'))

@bp.route('/user/<int:user_id>/activate', methods=['POST'])
@login_required
@admin_required # Asegúrate que este decorador esté definido y funcione
def activate_user(user_id):
    user_to_activate = User.query.get_or_404(user_id)

    if user_to_activate.id == current_user.id: 
        flash('No necesita activar su propia cuenta; ya está activa.', 'info')
        return redirect(url_for('admin.manage_users'))

    if user_to_activate.esta_activo:
        flash(f'El usuario {user_to_activate.username} ya está activo.', 'info')
    else:
        user_to_activate.esta_activo = True
        db.session.commit()
        flash(f'El usuario {user_to_activate.username} ha sido activado.', 'success')
        
    return redirect(url_for('admin.manage_users'))

#@bp.route('/user/<int:user_id>/toggle_active', methods=['POST'])
#@login_required
#def toggle_user_active_status(user_id):
#    if not current_user.is_authenticated or current_user.role != 'admin':
#        abort(403)
#    user_to_toggle = User.query.get_or_404(user_id)
#    if user_to_toggle.id == current_user.id:
#        flash('No puede cambiar su propio estado de activación.', 'danger')
#        return redirect(url_for('admin.manage_users'))
#    
#    user_to_toggle.esta_activo = not user_to_toggle.esta_activo
#    new_status_text = "activado" if user_to_toggle.esta_activo else "desactivado"
#    # Opcional: Registrar en HistorialMovimiento aquí (requeriría que HistorialMovimiento.cylinder_id sea nullable)
#    try:
#        db.session.commit()
#        flash(f'El usuario {user_to_toggle.username} ha sido {new_status_text} exitosamente.', 'success')
#    except Exception as e:
#        db.session.rollback()
#        flash(f'Error al cambiar el estado del usuario: {str(e)}', 'danger')
#    return redirect(url_for('admin.manage_users'))                           
