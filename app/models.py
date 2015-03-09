from mongoengine import *
from app import cifrado
import datetime

LETRAS = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')

"""
NOTA IMPORTANTE
En mongoengine no puede haber unique en documentos heredados, debe hacerse 
a traves de un sparse index
"""

class Usuario (Document):
    """ Clase base para la creacion del resto de usuarios """

    dni_numero = IntField (max_value = 99999999, min_value = 0, unique = True)
    dni_letra = StringField (max_length = 1, choices = LETRAS)
    nombre = StringField (max_length = 25)
    apellidos = StringField (max_length = 25)
    login = StringField (max_length = 8, unique =True, required = True)
    password = StringField (min_length = 4, required = True)
	# la fecha de registro se incluira al crear un usuario
    fecha_registro = DateTimeField (default = datetime.datetime.now)

    # todos los usuarios se almacenaran en la coleccion Usuario
    meta = {'allow_inheritance': True}

    # integracion con Flask-login
    def is_authenticated (self):
        return True

    def is_active (self):
        return True

    def is_anonymous (self):
        return False

    def get_id (self):
        return str (self.id)

    # Required for administrative interface
    def __unicode__ (self):
        return self.login

    ## cifrado de password
    def is_correct_password(self, plaintext):
        return cifrado.check_password_hash(self.password, plaintext)        

class Titulacion (EmbeddedDocument):
    """ Las titulaciones son documentos embebidos en los objetos Alumno """

    #codigo_titulacion = IntField (max_value = 99, min_value = 1, required = True)
    nombre = StringField (max_length = 50)
    centro = StringField (max_length = 50)        

class Alumno (Usuario):
    """ Establece las diferentes propiedades de un Alumno """

    numero_expediente = IntField (max_value = 9999, required = True)
    creditos_superados = IntField (max_value = 9999)
    curso = StringField (choices = ('1', '2', '3', '4'))
    cp = StringField (max_length = 5)
    telefono = ListField (StringField (max_length = 9))
    direccion = StringField (max_length = 50)
    localidad = StringField (max_length = 50)
    provincia = StringField (max_length = 25)
    email = EmailField ()
    #documento embebido titulaciones
    titulaciones = ListField(EmbeddedDocumentField(Titulacion))
    #relacion con proyectos
    #proyectos = ListField(ReferenceField('Proyecto', reverse_delete_rule= NULLIFY))
    numero_proyectos = IntField (choices = (1, 2), default = 1)

    meta =  {
                'indexes':  [
                                {
                                    # numero_expediente puede ser nulo, pero si se da, debe ser unico
                                    'fields': ['numero_expediente'],
                                    'unique': True,
                                    'sparse': True,
                                    'types': False,
                                },

                                {
                                    # email puede ser nulo, pero si se da, debe ser unico
                                    'fields': ['email'],
                                    'unique': True,
                                    'sparse': True,
                                    'types': False,
                                },                                
                            ],
            }         

class Profesor (Usuario):
    """ Establece las diferentes propiedades de un Profesor """

    departamento = StringField (max_length = 50)
    # atributo heredado de la relacion con la entidad Proyecto	
    rol_proyecto = StringField (choices = ('Tutor', 'Cotutor'))
	# atributo heredado de la relacion con la entidad Tribunal
    rol_tribunal = StringField (choices = ('Presidente', 'Vocal', 'Secretario', 'Suplente'))
    # relacion con la entidad Proyectos (definida al final del documento)
    #proyectos = ListField(ReferenceField('Proyecto', reverse_delete_rule= NULLIFY))
    # relacion con tribunales
    #tribunales = ListField(ReferenceField('Tribunal', reverse_delete_rule= NULLIFY))
   

class Tribunal(EmbeddedDocument):
    """ Establece las diferentes propiedades de un Tribunal """

    # el codigo de tribunal pasa a ser trivial al disponer de ObjectId()
    #codigo_tribunal = IntField (max_length = 2, required = True)
    miembros = DictField()	
    comentarios = StringField (max_length = 100)


class Proyecto (Document):
    """ Establece las diferentes propiedades de un Proyecto """

    fecha_oferta = DateTimeField (default = datetime.datetime.now)
    # el codigo de proyecto pasa a ser trivial al disponer de ObjectId()
    #codigo_proyecto = IntField (max_length = 3, required = True)
	
    titulo = StringField (max_length = 50, min_length = 1, required = True, unique = True)
    descripcion = StringField (max_length = 255, min_length = 1, required = True)
    estado = StringField (required = True, choices = ('SIN ASIGNAR', 'ASIGNADO', 'CERRADO'), default = 'SIN ASIGNAR')
    plazas = IntField (choices = (0, 1, 2), default = 1)
    nota = DecimalField (min_value = 0, max_value = 10, precision = 2, default = 0.0)
    matricula_honor = BooleanField (default = False)
    fecha_evaluacion = DateTimeField (default = datetime.datetime.now)
    lugar = StringField (max_length = 50, default = 'Campus URJC')
    # relacion con la entidad Alumnos
    alumnos = ListField (ReferenceField ('Alumno', reverse_delete_rule = NULLIFY))
    # relacion con la entidad Profesores (tutores o cotutores) 
    profesores = ListField (ReferenceField ('Profesor', reverse_delete_rule=NULLIFY)) 
    tribunal = EmbeddedDocumentField(Tribunal)     

class Externo (Usuario):
    """ Establece las diferentes propiedades de un Externo

    institucion = StringField(max_length = 25)
	# atributo heredado de la relacion con la entidad Tribunal
    rol_tribunal = StringField (choices = ('Presidente', 'Vocal', 'Secretario', 'Suplente'))
    tribunales = ListField (ReferenceField ('Tribunal', reverse_delete_rule=NULLIFY))
    """

# Interrelaciones definidas al final para evitar referencias circulares
Alumno.proyectos = ListField (ReferenceField ('Proyecto', reverse_delete_rule= NULLIFY)) 
Profesor.proyectos = ListField (ReferenceField ('Proyecto'))