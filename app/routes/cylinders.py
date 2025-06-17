from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.cylinder import Cylinder
from app.models.user import User # Needed for potential assignments or logging
from app.forms import CreateCylinderForm, UpdateCylinderStatusForm
from datetime import datetime

bp = Blueprint('cylinders', __name__)

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    # Order by creation date, newest first
    cylinders_pagination = Cylinder.query.order_by(Cylinder.creation_date.desc()).paginate(page=page, per_page=10, error_out=False)
    next_url = url_for('cylinders.index', page=cylinders_pagination.next_num) if cylinders_pagination.has_next else None
    prev_url = url_for('cylinders.index', page=cylinders_pagination.prev_num) if cylinders_pagination.has_prev else None

    return render_template('cylinders/index.html', title='Oxygen Cylinders',
                           cylinders=cylinders_pagination.items,
                           next_url=next_url, prev_url=prev_url,
                           pagination=cylinders_pagination)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_cylinder():
    form = CreateCylinderForm()
    if form.validate_on_submit():
        cylinder = Cylinder(cylinder_id_tag=form.cylinder_id_tag.data, status='available') # Default to 'available' on creation
        db.session.add(cylinder)
        db.session.commit()
        flash(f'Cylinder {cylinder.cylinder_id_tag} has been created successfully!', 'success')
        return redirect(url_for('cylinders.index'))
    return render_template('cylinders/create_cylinder.html', title='Create New Cylinder', form=form)

@bp.route('/<int:cylinder_id>')
@login_required
def view_cylinder(cylinder_id):
    cylinder = Cylinder.query.get_or_404(cylinder_id)
    return render_template('cylinders/view_cylinder.html', title=f'Cylinder {cylinder.cylinder_id_tag}', cylinder=cylinder)

@bp.route('/<int:cylinder_id>/update_status', methods=['GET', 'POST'])
@login_required
def update_cylinder_status(cylinder_id):
    cylinder = Cylinder.query.get_or_404(cylinder_id)
    form = UpdateCylinderStatusForm(obj=cylinder) # Pre-populate with current status

    if form.validate_on_submit():
        old_status = cylinder.status
        new_status = form.status.data
        cylinder.status = new_status

        if new_status == 'delivered' and old_status != 'delivered':
            cylinder.delivery_date = datetime.utcnow()
            cylinder.reception_date = None # Clear reception date if it was previously received
        elif new_status == 'received' and old_status != 'received':
            cylinder.reception_date = datetime.utcnow()
            # Optionally, clear delivery date if it makes sense for the workflow
            # cylinder.delivery_date = None
        elif new_status == 'available':
            # If it's made available, clear previous delivery/reception specific dates
            cylinder.delivery_date = None
            cylinder.reception_date = None

        db.session.commit()
        flash(f'Status for cylinder {cylinder.cylinder_id_tag} has been updated to {new_status}.', 'success')
        return redirect(url_for('cylinders.view_cylinder', cylinder_id=cylinder.id))

    return render_template('cylinders/update_cylinder_status.html',
                           title=f'Update Status for {cylinder.cylinder_id_tag}',
                           form=form, cylinder=cylinder)

# Admin specific cylinder actions (e.g., delete) could go in admin blueprint or here with admin_required
@bp.route('/<int:cylinder_id>/delete', methods=['POST'])
@login_required # Consider making this admin_required
def delete_cylinder(cylinder_id):
    # Ensure only admins can delete, or add more sophisticated permission checks
    if current_user.role != 'admin':
        abort(403)

    cylinder = Cylinder.query.get_or_404(cylinder_id)
    # Add checks here: e.g., a cylinder that is 'delivered' should perhaps not be deletable directly
    # Or require it to be 'available' or 'maintenance'
    # For now, direct delete:
    db.session.delete(cylinder)
    db.session.commit()
    flash(f'Cylinder {cylinder.cylinder_id_tag} has been deleted.', 'success')
    return redirect(url_for('cylinders.index'))
