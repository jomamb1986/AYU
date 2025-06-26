# <!-- este es el codigo para app/routes/auth.py con rutas de reseteo de contraseña PARTE 1 --> #}
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from app.forms import LoginForm, RegistrationForm, RequestPasswordResetForm, PasswordResetForm # Nuevos forms añadidos
from app.models.user import User # Modelo User con métodos de token
from app import db
from flask_login import login_user, logout_user, current_user, login_required
from app.models.historial import HistorialMovimiento
from datetime import datetime

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Usuario o contraseña incorrectos. Intente de nuevo.', 'danger')
            return redirect(url_for('auth.login'))
        if not user.is_active:
            flash('Esta cuenta de usuario ha sido desactivada y no puede iniciar sesión.', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            if user.role == 'admin':
                next_page = url_for('admin.dashboard')
            else:
                next_page = url_for('main.dashboard')
        flash(f'¡Bienvenido de nuevo, {user.username}!', 'success')
        return redirect(next_page)
    return render_template('auth/login.html', title='Iniciar Sesión', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ha cerrado sesión exitosamente.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, 
                    email=form.email.data, 
                    nombre=form.nombre.data, 
                    apellidos=form.apellidos.data)
        user.set_password(form.password.data)
        if User.query.count() == 0:
            user.role = 'admin'
            flash('¡Felicidades, es el primer usuario administrador registrado!', 'success')
        else:
            user.role = 'user'
            flash('¡Felicidades, se ha registrado exitosamente!', 'success')
        db.session.add(user)
        db.session.commit()
        flash('Ahora puede iniciar sesión.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Registrarse', form=form)

# --- NUEVAS RUTAS PARA RESTABLECER CONTRASEÑA ---

@bp.route('/request_password_reset', methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_reset_password_token()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            print("-" * 80)
            print("ENLACE PARA RESTABLECER CONTRASEÑA (COPIAR Y PEGAR EN NAVEGADOR):")
            print(reset_url)
            print("-" * 80)
            flash('Se ha "enviado" un enlace para restablecer su contraseña a su correo (verifique la consola del servidor Flask).', 'info')
        else:
            flash('Si su correo está registrado, recibirá un enlace para restablecer su contraseña en breve (verifique la consola del servidor).', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/request_password_reset.html', 
                           title='Solicitar Restablecimiento de Contraseña', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('El enlace para restablecer la contraseña es inválido o ha expirado.', 'warning')
        return redirect(url_for('auth.login'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Su contraseña ha sido restablecida exitosamente. Ahora puede iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', 
                           title='Restablecer Contraseña', form=form, token=token)
