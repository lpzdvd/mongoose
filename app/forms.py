from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, IntegerField, SelectField, DecimalField, BooleanField, DateTimeField, validators
from wtforms.widgets import TextArea
from wtforms.validators import Required, NumberRange, Length, Email, EqualTo, DataRequired, ValidationError
from app import cifrado

from models import Usuario, Proyecto

class UserForm(Form):
    """ Formulario base para la creacion de los formularios 
    de registro de profesores y alumnos """

    dni_numero = IntegerField('DNI', 
        [Required(
            message = 'Debe ser un entero'),
        NumberRange(
            min=0, max=99999999, message='El valor debe ser entre 0 y 99999999')
        ])

    dni_letra = SelectField('Letra',
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'),
         ('F', 'F'), ('G', 'G'), ('H', 'H'), ('I', 'I'), ('J', 'J'),
         ('K', 'K'), ('L', 'L'),('M', 'M'), ('N', 'N'),('O', 'O'), ('P', 'P'),
         ('Q', 'Q'), ('R', 'R'),('S', 'S'), ('T', 'T'),('U', 'U'), ('V', 'V'),
         ('W', 'W'), ('X', 'X'),('Y', 'Y'), ('Z', 'Z')],
         validators = [Required('Campo obligatorio')])

    nombre = TextField('Nombre', 
        [Required(
            message = 'Campo obligatorio'), 
        Length(min = 1, max = 25, message = 'El nombre no puede exceder 25 caracteres')
        ])

    apellidos = TextField('Apellidos', 
        [Required(
            message = 'Campo obligatorio'),
        Length(min = 1, max = 25, message = 'El apellido no puede exceder 25 caracteres')
        ])

    login = TextField('Login', 
        [Required(
            message = 'Campo obligatorio'),
        Length(min = 1, max = 8, message ='El login no puede exceder 8 caracteres')
        ])

    password = PasswordField('Password',
        [Required(
            message = 'Campo obligatorio'),
        Length(min = 4, max = 8, message = 'El password debe tener entre 4 y 8 caracteres'),
        EqualTo('confirmar', message = 'Ambos campos deben coincidir')
        ])

    confirmar = PasswordField('Confirmar', 
        [Required(
            message = 'Campo obligatorio'),
        Length(min = 4, max = 8, message = 'El password debe tener entre 4 y 8 caracteres')])

class AlumnoForm(UserForm):
    """ Formulario usado por el registro de alumnos """

    numero_expediente = IntegerField('Numero de Expediente', 
        [Required(
            message = 'Debe ser un entero'),
        NumberRange(min = 1, max = 9999, message= 'El valor debe ser entre 1 y 9999')
        ])

    creditos_superados = IntegerField('Creditos superados', 
        [Required(
            message = 'Debe ser un entero'),
        NumberRange(min = 0, max = 240, message='El valor debe ser entre 0 y 240')
        ])

    curso = SelectField('Curso', 
        choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')],
        validators = [Required('Campo obligatorio')])

    cp = TextField('CP', 
        [Required(
            message = 'Campo obligatorio'),
        Length(min = 1, max = 5, message ='No puede exceder 5 caracteres')
        ])

    telefono = TextField('Telefono', 
        [Required(
            message = 'Campo obligatorio'), 
        Length(min = 1, max = 9, message = 'No puede exceder 9 caracteres')
        ])

    direccion = TextField('Direccion', 
        [Required(
            message = 'Campo obligatorio'),
        Length(min = 1, max = 50, message = 'No puede exceder 50 caracteres')
        ])

    localidad = TextField('Localidad', 
        [Required(message = 'Campo obligatorio'),
        Length(min = 1, max = 50, message = 'No puede exceder 50 caracteres')
        ])

    provincia = TextField('Provincia', 
        [Required(
            message = 'Campo obligatorio'),
        Length(min = 1, max = 25, message = 'No puede exceder 25 caracteres')
        ])

    email = TextField('Email', 
        [Required(
            message = 'Campo obligatorio'),
        Email(message = 'No es una direccion de correo valida')
        ])

    # documentos emebebidos: titulaciones
    titulacion_nombre = TextField('Titulacion', 
        [Required(message = 'Campo obligatorio'),
        Length(min = 1, max = 50, message = 'No puede exceder 50 caracteres')
        ])

    titulacion_centro = TextField('Centro', 
        [Required(message = 'Campo obligatorio'),
        Length(min = 1, max = 50, message = 'No puede exceder 50 caracteres')
        ])   

    # pero en doble grado esta informacion es opcional
    titulacion2_nombre = TextField('Titulacion (*)', 
        [Length(max = 50, message = 'No puede exceder 50 caracteres')
        ])

    titulacion2_centro = TextField('Centro (*)', 
        [Length(max = 50, message = 'No puede exceder 50 caracteres')
        ])

    # control del numero de proyectos         
    numero_proyectos = SelectField('Proyectos a desarrollar', coerce=int,
        choices=[(1, 1), (2, 2)])
		
class ProfesorForm(UserForm):
    """ Formulario del registro de profesores """

    departamento = SelectField('Departamento',
        choices=[('Ciencias de la Computacion', 'Ciencias de la Computacion'),
                ('Arquitectura de la Computacion', 'Arquitectura de la Computacion'),
                ('Lenguajes y Sistemas Informaticos', 'Lenguajes y Sistemas Informaticos'),
                ('Estadistica e Investigacion Operativa', 'Estadistica e Investigacion Operativa')],
        validators = [Required('Campo obligatorio')])

class LoginForm (Form):
    """ Formulario de login en la barra de navegacion.
    Usado por todas las vistas """

    login = TextField('login', 
        [Required(
            message = 'Campo obligatorio')
        ])

    password = PasswordField('password', 
        [Required(
            message = 'Campo obligatorio')
        ])

    #remember_me = BooleanField('remember_me', default = False)
    
    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise ValidationError('*** Invalid user ***')

        if not user.is_correct_password(self.password.data):
            raise ValidationError('*** Invalid password ***')
    
    def get_user(self):
        return Usuario.objects(login=self.login.data).first() 

class ProyectoForm(Form):
    """ Formulario de alta de nuevos proyectos """
    titulo = TextField('Titulo', 
        [Required(
            message = 'Campo obligatorio'),
        Length(min = 1, max = 50, message = 'El titulo del proyecto debe ser informado')
        ])
    
    # para la descripcion he usado un widget de wtforms para poder renderizar
    # un TextArea y poder establecer filas. 
    descripcion = TextField('Descripcion', 
        [Required(
            message = 'Campo obligatorio'),
        Length(min = 1, max = 255, message = 'La descripcion del proyecto ha de ser informada')
        ], widget = TextArea())

    # es necesario coerce para que acepte el entero
    plazas = SelectField('Plazas ofertadas', coerce=int,
        choices=[(0, 0), (1, 1), (2, 2)])
		
class ProyectoEditForm (ProyectoForm):
    """ Formulario del edicion de proyectos """
	
    # Inicialmente SIN ASIGNAR. Editable	
    estado = SelectField('Estado del proyecto',
        choices=[('SIN ASIGNAR', 'SIN ASIGNAR'),
                ('ASIGNADO', 'ASIGNADO'),
                ('CERRADO', 'CERRADO')])

    # Inicialmente es 0.0. Editable
    nota = DecimalField('Calificacion', [NumberRange(min = 0, max = 10, message = 'Fuera de rango')])
	
    # inicialmente False. Editable.
    matricula_honor = BooleanField('Se propone para Matricula de Honor')
	
    fecha_evaluacion = DateTimeField('Fecha de evaluacion')
	
    lugar = TextField('Lugar de evaluacion', 
        [Length(min = 1, max = 255, message = 'Campo vacio')
        ])
		
	#TODO: alumnos
	#TODO: profesores

class AlumnoEditForm(Form):
    """ Formulario de edicion de alumno
    NOTA: quiza haya otra forma mas elegante de hacerlo resusando los anteriores
    pero cerca del final del desarrollo queda como mejora. El problema reside
    en que a diferencia de AlumnoForm, un alumno no deberia poder editar 
    sus titulaciones """

    dni_numero = IntegerField('DNI', 
        [Required(
            message = 'Debe ser un entero'),
        NumberRange(
            min=0, max=99999999, message='El valor debe ser entre 0 y 99999999')
        ])

    dni_letra = SelectField('Letra',
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'),
         ('F', 'F'), ('G', 'G'), ('H', 'H'), ('I', 'I'), ('J', 'J'),
         ('K', 'K'), ('L', 'L'),('M', 'M'), ('N', 'N'),('O', 'O'), ('P', 'P'),
         ('Q', 'Q'), ('R', 'R'),('S', 'S'), ('T', 'T'),('U', 'U'), ('V', 'V'),
         ('W', 'W'), ('X', 'X'),('Y', 'Y'), ('Z', 'Z')],
         validators = [Required('Campo obligatorio')])

    nombre = TextField('Nombre', 
        [Required(
            message = 'Campo obligatorio'), 
        Length(min = 1, max = 25, message = 'El nombre no puede exceder 25 caracteres')
        ])

    apellidos = TextField('Apellidos', 
        [Required(
            message = 'Campo obligatorio'),
        Length(min = 1, max = 25, message = 'El apellido no puede exceder 25 caracteres')
        ])

    numero_expediente = IntegerField('Numero de Expediente', 
        [Required(
            message = 'Debe ser un entero'),
        NumberRange(min = 1, max = 9999, message= 'El valor debe ser entre 1 y 9999')
        ])

    creditos_superados = IntegerField('Creditos superados', 
        [Required(
            message = 'Debe ser un entero'),
        NumberRange(min = 0, max = 240, message='El valor debe ser entre 0 y 240')
        ])

    curso = SelectField('Curso', 
        choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')],
        validators = [Required('Campo obligatorio')])

    cp = TextField('CP', 
        [Required(
            message = 'Campo obligatorio'),
        Length(min = 1, max = 5, message ='No puede exceder 5 caracteres')
        ])

    direccion = TextField('Direccion', 
        [Required(
            message = 'Campo obligatorio'),
        Length(min = 1, max = 50, message = 'No puede exceder 50 caracteres')
        ])

    localidad = TextField('Localidad', 
        [Required(message = 'Campo obligatorio'),
        Length(min = 1, max = 50, message = 'No puede exceder 50 caracteres')
        ])

    provincia = TextField('Provincia', 
        [Required(
            message = 'Campo obligatorio'),
        Length(min = 1, max = 25, message = 'No puede exceder 25 caracteres')
        ])

    email = TextField('Email', 
        [Required(
            message = 'Campo obligatorio'),
        Email(message = 'No es una direccion de correo valida')
        ])