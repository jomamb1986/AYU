# <!-- este es el codigo para app/forms.py con formularios de reseteo de contraseña PARTE 1 --> #}
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, HiddenField, DateField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Optional

from app.models.user import User
from app.models.cylinder import Cylinder

def date_check(form, field):
    if form.fecha_inicio.data and field.data: 
        if field.data < form.fecha_inicio.data:
            raise ValidationError('La fecha de fin no puede ser anterior a la fecha de inicio.')
class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(message="El nombre de usuario es requerido.")])
    password = PasswordField('Contraseña', validators=[DataRequired(message="La contraseña es requerida.")])
    remember_me = BooleanField('Recuérdame')
    submit_button = SubmitField('Iniciar Sesión') # Renamed 'submit' to 'submit_button'

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(message="El nombre de usuario es requerido."), Length(min=3, max=64, message="Debe tener entre 3 y 64 caracteres.")])
    nombre = StringField('Nombre(s)', validators=[DataRequired(message="El nombre es requerido."), Length(min=2, max=64)])
    apellidos = StringField('Apellidos', validators=[DataRequired(message="Los apellidos son requeridos."), Length(min=2, max=128)])
    email = StringField('Correo Electrónico', validators=[DataRequired(message="El correo es requerido."), Email(message="Correo electrónico no válido.")])
    password = PasswordField('Contraseña', validators=[DataRequired(message="La contraseña es requerida."), Length(min=6, max=128, message="Debe tener entre 6 y 128 caracteres.")])
    password2 = PasswordField(
        'Repetir Contraseña', validators=[DataRequired(message="Repita la contraseña."), EqualTo('password', message='Las contraseñas deben coincidir.')])
    submit_button = SubmitField('Registrarse') # Renamed 'submit' to 'submit_button'

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Este nombre de usuario ya está en uso. Por favor, elija otro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Esta dirección de correo ya está registrada. Por favor, use otra.')
class EditUserRoleForm(FlaskForm):
    role = SelectField('Rol', choices=[('user', 'Usuario'), ('admin', 'Administrador')], validators=[DataRequired()])
    submit = SubmitField('Actualizar Rol')

class CreateCylinderForm(FlaskForm):
    cylinder_id_tag = StringField('ID del Botellón (Etiqueta Principal)', validators=[DataRequired(message="El ID del botellón es requerido."), Length(min=3, max=64)])
    marca = StringField('Marca', validators=[Optional(), Length(max=80)])
    color = StringField('Color', validators=[Optional(), Length(max=50)])
    numero_serie = StringField('Número de Serie (Opcional)', validators=[Optional(), Length(max=80)])
    submit = SubmitField('Crear Botellón')

    def validate_cylinder_id_tag(self, cylinder_id_tag):
        cylinder = Cylinder.query.filter_by(cylinder_id_tag=cylinder_id_tag.data).first()
        if cylinder is not None:
            raise ValidationError('Este ID de botellón (Etiqueta Principal) ya está registrado.')

class UpdateCylinderStatusForm(FlaskForm):
    status = SelectField('Nuevo Estado Transaccional', choices=[
        ('delivered', 'Entregado'),
        ('received', 'Recibido'),
    ], validators=[DataRequired(message="Seleccione un nuevo estado.")])
    nombre_contraparte = StringField('Entregado a / Recibido de (Nombre)', validators=[DataRequired(message="El nombre de la contraparte es requerido."), Length(max=150)])
    nota_movimiento = TextAreaField('Nota Adicional sobre el Movimiento (Opcional)', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Actualizar Estado y Registrar Movimiento')

class BatchProcessForm(FlaskForm):
    nombre_contraparte = StringField('Nombre de Destinatario/Remitente del Lote', 
                                     validators=[DataRequired(message="El nombre de la contraparte es requerido para el lote."), 
                                                 Length(max=150)])
    nota_movimiento = TextAreaField('Nota Adicional para el Lote (Opcional)', 
                                    validators=[Optional(), Length(max=500)])
    selected_ids_csv = HiddenField(validators=[DataRequired(message="No se seleccionaron botellones.")])
    action_type = HiddenField(validators=[DataRequired(message="No se especificó la acción.")])
    submit = SubmitField('Confirmar y Procesar Lote')
class DateRangeReportForm(FlaskForm):
    fecha_inicio = DateField('Fecha de Inicio (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    fecha_fin = DateField('Fecha de Fin (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional(), date_check])
    submit_filter = SubmitField('Filtrar Reporte')
    clear_filter = SubmitField('Limpiar Filtro')

class EditCylinderForm(FlaskForm):
    marca = StringField('Marca', validators=[Optional(), Length(max=80)])
    color = StringField('Color', validators=[Optional(), Length(max=50)])
    numero_serie = StringField('Número de Serie', validators=[Optional(), Length(max=80)])
    status = SelectField('Estado General', choices=[
        ('available', 'Disponible'),
        ('maintenance', 'Mantenimiento'),
    ], validators=[DataRequired(message="Seleccione un estado.")])
    nota_edicion = TextAreaField('Nota sobre la Edición (Opcional, se guardará en el historial)', validators=[Optional(), Length(max=500)])
    submit_button = SubmitField('Guardar Cambios') # Renamed 'submit' to 'submit_button' to avoid conflict with the tool name

    # def __init__(self, original_numero_serie, *args, **kwargs):
    #     super(EditCylinderForm, self).__init__(*args, **kwargs)
    #     self.original_numero_serie = original_numero_serie

    # def validate_numero_serie(self, numero_serie):
    #     if numero_serie.data and numero_serie.data != self.original_numero_serie:
    #         cylinder = Cylinder.query.filter_by(numero_serie=numero_serie.data).first()
    #         if cylinder:
    #             raise ValidationError('Este Número de Serie ya está registrado para otro botellón.')
# --- NUEVOS FORMULARIOS PARA RESTABLECER CONTRASEÑA ---
class RequestPasswordResetForm(FlaskForm):
    email = StringField('Su Correo Electrónico Registrado', 
                        validators=[DataRequired(message="El correo es requerido."), 
                                    Email(message="Correo electrónico no válido.")])
    submit = SubmitField('Solicitar Restablecimiento')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Nueva Contraseña', 
                             validators=[DataRequired(message="La nueva contraseña es requerida."), 
                                         Length(min=6, message="Debe tener al menos 6 caracteres.")])
    password2 = PasswordField(
        'Confirmar Nueva Contraseña', 
        validators=[DataRequired(message="Confirme la nueva contraseña."), 
                    EqualTo('password', message='Ambas contraseñas deben coincidir.')])
    submit = SubmitField('Restablecer Contraseña')
# --- FIN DE NUEVOS FORMULARIOS ---
            
