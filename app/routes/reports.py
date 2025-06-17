from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models.cylinder import Cylinder
from app import db # For more complex queries if needed
from datetime import datetime, timedelta

bp = Blueprint('reports', __name__)

@bp.route('/')
@login_required
def index():
    # A simple landing page for reports, could list available reports
    return render_template('reports/index.html', title='Reports')

@bp.route('/creations')
@login_required
def cylinder_creations_report():
    page = request.args.get('page', 1, type=int)
    # Query all cylinders ordered by creation_date
    creations_pagination = Cylinder.query.order_by(Cylinder.creation_date.desc()).paginate(page=page, per_page=15, error_out=False)

    next_url = url_for('reports.cylinder_creations_report', page=creations_pagination.next_num) if creations_pagination.has_next else None
    prev_url = url_for('reports.cylinder_creations_report', page=creations_pagination.prev_num) if creations_pagination.has_prev else None

    return render_template('reports/creations_report.html',
                           title='Cylinder Creations Report',
                           cylinders=creations_pagination.items,
                           pagination=creations_pagination,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/receptions')
@login_required
def cylinder_receptions_report():
    page = request.args.get('page', 1, type=int)
    # Query cylinders that have a reception_date, ordered by reception_date
    receptions_pagination = Cylinder.query.filter(Cylinder.reception_date.isnot(None))                                     .order_by(Cylinder.reception_date.desc())                                     .paginate(page=page, per_page=15, error_out=False)

    next_url = url_for('reports.cylinder_receptions_report', page=receptions_pagination.next_num) if receptions_pagination.has_next else None
    prev_url = url_for('reports.cylinder_receptions_report', page=receptions_pagination.prev_num) if receptions_pagination.has_prev else None

    return render_template('reports/receptions_report.html',
                           title='Cylinder Receptions Report',
                           cylinders=receptions_pagination.items,
                           pagination=receptions_pagination,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/deliveries')
@login_required
def cylinder_deliveries_report():
    page = request.args.get('page', 1, type=int)
    # Query cylinders that have a delivery_date, ordered by delivery_date
    deliveries_pagination = Cylinder.query.filter(Cylinder.delivery_date.isnot(None))                                     .order_by(Cylinder.delivery_date.desc())                                     .paginate(page=page, per_page=15, error_out=False)

    next_url = url_for('reports.cylinder_deliveries_report', page=deliveries_pagination.next_num) if deliveries_pagination.has_next else None
    prev_url = url_for('reports.cylinder_deliveries_report', page=deliveries_pagination.prev_num) if deliveries_pagination.has_prev else None

    return render_template('reports/deliveries_report.html',
                           title='Cylinder Deliveries Report',
                           cylinders=deliveries_pagination.items,
                           pagination=deliveries_pagination,
                           next_url=next_url, prev_url=prev_url)
