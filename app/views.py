from app import app, lm, cifrado
from flask import render_template, redirect, url_for, request, g, flash
from flask.ext import login
from forms import LoginForm, UserForm, AlumnoForm, AlumnoEditForm, ProfesorForm, ProyectoForm, ProyectoEditForm
from models import Usuario, Alumno, Profesor, Proyecto, Titulacion, Tribunal


def contar_proyectos():
    """ Devuelve el numero de proyectos dados de alta en la aplicacion """
    return len(Proyecto.objects.all())

def es_admin():
    """ Comprueba si el usuario logado es admin """
    if str(g.user) == 'admin':
        return True
    else:
        return False

@lm.user_loader
def load_user(user_id):
    """ Metodo requerido por la extension flask-login """
    return Usuario.objects(id=user_id).first()


@app.before_request
def before_request():
    """ Antes de cada request almacena en g el usuario actual
    Cualquier funcion decorada de esta manera se ejecutara
	antes de cada vista
    """
    g.user = login.current_user

@app.route('/')
def index_view():
    """ Redirige cada request al root de la aplicacion a la vista de login """
    return redirect(url_for('login_view'))

@app.route('/profesor', methods = ('GET', 'POST'))
@login.login_required
def profesor_view():
    """ Vista para el registro de profesores """

    if not es_admin():
        mensaje = 'Restringido al administrador'
        flash(mensaje)
        return redirect(url_for('login_view'))

    form = ProfesorForm()

    if request.method == 'POST' and form.validate_on_submit():
        # alta del profesor en la base de datos
        u = Profesor(dni_numero = form.dni_numero.data,
            dni_letra = form.dni_letra.data,
            nombre = form.nombre.data,
            apellidos = form.apellidos.data,
            login = form.login.data,
            password = cifrado.generate_password_hash(form.password.data),
            departamento = form.departamento.data)
        u.save()

        return redirect(url_for('login_view'))        

    return render_template('profesor.html', form = form)
	
@app.route('/alumno', methods = ('GET', 'POST'))
@login.login_required
def alumno_view():
    """ Vista para el registro de alumnos """

    if not es_admin():
        mensaje = 'Restringido al administrador'
        flash(mensaje)        
        return redirect(url_for('login_view'))

    form = AlumnoForm()
    if request.method == 'POST' and form.validate_on_submit():
        # NOTAS AL CREAR UN ALUMNO
		# telefono: al crear el alumno facilito uno, pero puede haber varios...
		#                 es un detalle a pulir
		# titulacion: al crear el alumno crea un Array para ello, pero esta vacio
        #             lo ideal es tener una vista que realice el alta de titulaciones, 
        #             pasar la query con todas y que aparezca un desplegable.
        #               EN EL MENU DE ALUMNO DEBERIA PODER EDITARSE
		# proyectos: no se crean al registrar el alumno, lo asociare mas tarde.

        t1 = Titulacion(nombre = form.titulacion_nombre.data,
            centro = form.titulacion_centro.data)

        t2 = Titulacion(nombre = form.titulacion2_nombre.data,
            centro = form.titulacion2_centro.data)        


        u = Alumno(dni_numero = form.dni_numero.data,
            dni_letra = form.dni_letra.data,
            nombre = form.nombre.data,
            apellidos = form.apellidos.data,
            login = form.login.data,
            password = cifrado.generate_password_hash(form.password.data),
			numero_expediente = form.numero_expediente.data,
			creditos_superados = form.creditos_superados.data,
			curso = form.curso.data,
			cp = form.cp.data,
			telefono = [form.telefono.data],
			direccion = form.direccion.data,
			localidad = form.localidad.data,
			provincia = form.provincia.data,
			email = form.email.data,
            titulaciones = [t1, t2],
            numero_proyectos = form.numero_proyectos.data)

        u.save()
        return redirect(url_for('login_view'))        

    return render_template('alumno.html', form = form)	

@app.route('/login', methods = ('GET', 'POST'))
def login_view():
    """ Vista de login (portada de Mongoose) """
    
    # hay que considerar que un usuario ya puede haber sido autenticado por el sistema
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home_view', user = g.user))

    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        user = form.get_user()
        login.login_user(user)

        # feedback al usuario
        mensaje = 'Por favor, utilice las opciones del menu lateral'
        flash(mensaje)

        return redirect(url_for('home_view', user = g.user))

    return render_template('login.html', form = form, user = g.user)

@app.route('/logout')
def logout_view():
    """ Vista de logout (redirige al login) """

    login.logout_user()
    return redirect(url_for('index_view'))

@app.route('/home/<user>')
@login.login_required
def home_view(user):
    """ Vista del home de un usuario """

    form = LoginForm()
    return render_template('home.html', form = form, user = g.user, proyectos_totales = contar_proyectos())

@app.route('/proyectos/alta', methods = ('GET', 'POST'))
@login.login_required
def proyectos_alta_view():
    """ Vista de alta de un proyecto. """

    form = LoginForm()
    formulario_proyecto = ProyectoForm()

    if request.method == 'POST' and formulario_proyecto.validate_on_submit():
        # al crear el proyecto damos de alta al profesor
        profesores = []
        profesores.append(g.user.id)

        # alta del profesor en la base de datos
        p = Proyecto(titulo = formulario_proyecto.titulo.data,
            descripcion = formulario_proyecto.descripcion.data,
            plazas = formulario_proyecto.plazas.data,
            profesores = profesores)
        p.save()

        # informar al usuario
        mensaje = 'Creado proyecto con identificador ' + str (p.id)
        flash(mensaje)

        return redirect(url_for('home_view', user = g.user))          
           
    return render_template('proyectos_alta.html',
        form = form,
        proyecto = formulario_proyecto,
        user = g.user,
        proyectos_totales = contar_proyectos()) 

@app.route('/proyectos/baja', methods = ('GET', 'POST'))
@login.login_required
def proyectos_baja_view():
    """ Vista de baja de proyectos """

    form = LoginForm()
    # busco todos los proyectos creados por ese profesor
    proyectos = Proyecto.objects(profesores = g.user.id).all()

    if request.method == 'POST':
        # obtengo el proyecto seleccionado en el formulario y lo borro
        p = Proyecto.objects(id = request.form['proyecto']).first()
        p.delete()

        # informar al usuario del proyecto eliminado
        mensaje = 'Eliminado proyecto con identificador ' + " " + str(p.id)
        flash(mensaje)

        return redirect(url_for('home_view', user = g.user)) 

    return render_template('proyectos_baja.html',
        form = form,
        proyectos = proyectos,
        user = g.user,
        proyectos_totales = contar_proyectos())

@app.route('/proyectos/seleccion', methods = ('GET', 'POST'))
@login.login_required
def proyectos_seleccion_view():
    """ Vista de seleccion de proyectos """

    form = LoginForm()
    # busco todos los proyectos creados por ese profesor
    proyectos = Proyecto.objects(profesores = g.user.id).all()

    if request.method == 'POST':
        # obtengo el proyecto seleccionado en el formulario
        p = Proyecto.objects(id = request.form['proyecto']).first()

        return redirect(url_for('proyectos_edicion_view', user = g.user, proyecto = p.id)) 

    return render_template('proyectos_seleccion.html',
        form = form,
        proyectos = proyectos,
        user = g.user,
        proyectos_totales = contar_proyectos())


@app.route('/proyectos/edicion/<proyecto>', methods = ('GET', 'POST'))
@login.login_required
def proyectos_edicion_view(proyecto):
    """ Vista de edicion de proyectos """

    form = LoginForm()

    # obtener el proyecto que vamos a editar
    p = Proyecto.objects(id = proyecto).first()

    formulario_proyecto = ProyectoEditForm(request.form, p)

    if request.method == 'POST' and formulario_proyecto.validate():    
        formulario_proyecto.populate_obj(p)
        p.save()

        # informar
        mensaje = 'Se ha editado el proyecto' + " " + str(p.id) + " " + '(' + p.titulo + ')'
        flash(mensaje)
        return redirect(url_for('home_view', user = g.user))

    return render_template('proyectos_edicion.html',
        form = form,
        user = g.user,
        proyectos_totales = contar_proyectos(),
        proyecto = p,
        formulario_proyecto = formulario_proyecto)

@app.route('/proyectos/listar')
@login.login_required
def proyectos_listar_view():
    """ Vista de lista de todos los proyectos """

    form = LoginForm()

    # obtener todos los proyectos
    proyectos = Proyecto.objects().all()

    # obtener el codigo de usuario del profesor
    profesor = Usuario.objects(login__exact = str(g.user)).first()

    return render_template('proyectos_listar.html',
        form = form,
        user = g.user,
        proyectos = proyectos,
        profesor = profesor,
        proyectos_totales = contar_proyectos())   

@app.route('/alumnos/edicion/<alumno>', methods = ('GET', 'POST'))
@login.login_required
def alumnos_edicion_view(alumno):
    """ Vista de edicion de alumnos """

    form = LoginForm()

    # obtener el proyecto que vamos a editar
    a = Usuario.objects(login = alumno).first()

    formulario_alumno = AlumnoEditForm(request.form, a)

    if request.method == 'POST' and formulario_alumno.validate():

        formulario_alumno.populate_obj(a)
        a.save()

        # informar
        mensaje = 'Se han editado satisfactoriamente los datos del usuario ' + str (g.user)
        flash(mensaje)
        return redirect(url_for('home_view', user = g.user))

    return render_template('alumnos_edicion.html',
        form = form,
        user = g.user,
        alumno = a,
        formulario_alumno = formulario_alumno)

@app.route('/proyectos/asignacion/<proyecto>', methods = ('GET', 'POST'))
@login.login_required
def proyectos_asignacion_view(proyecto):
    """ Vista de asignacion de un proyecto a 1 o 2 alumnos """

    form = LoginForm()

    # obtener el proyecto que hemos referenciado
    p = Proyecto.objects(id = proyecto).first()
    # obtener el alumno que intenta registrarse a un proyecto
    a = Alumno.objects(id = g.user.id).first()

    if a.numero_proyectos == 0:
        # redirigir al home
        mensaje = 'El alumno no puede ser asignado a mas proyectos'
        flash(mensaje)
        return redirect(url_for('home_view', user = g.user))


    # gestionar la asignacion (el proyecto siempre esta sin asignar al llegar a la vista)
    if (p.plazas == 2) and not(g.user.id in p.alumnos):
        # decremento una plaza. sigue sin asignar pero incluyo el id del alumno
        Proyecto.objects(id = p.id).update(dec__plazas=1,
            push__alumnos=g.user.id)
        # recargo el objeto para su uso
        p.reload()

        # control del numero de proyectos del alumno
        Alumno.objects(id = g.user.id).update(dec__numero_proyectos=1)
        a.reload()        

        # informar
        mensaje = 'El alumno ha sido asignado al proyecto'
        flash(mensaje)
        return redirect(url_for('home_view', user = g.user))

    if (p.plazas == 1) and not(g.user.id in p.alumnos):
        # no quedan plazas. queda asignado e incluyo el id del alumno.
        Proyecto.objects(id = p.id).update(set__plazas=0,
            set__estado = 'ASIGNADO',
            add_to_set__alumnos=g.user.id)
        #recargo el objeto para su uso
        p.reload()    

        # control del numero de proyectos del alumno
        Alumno.objects(id = g.user.id).update(dec__numero_proyectos=1)
        a.reload()

        # informar
        mensaje = 'Has sido asignado al proyecto'
        flash(mensaje)
        return redirect(url_for('home_view', user = g.user))

    return render_template('proyectos_asignacion.html',
        form = form,
        user = g.user,
        proyecto = proyecto)    

@app.route('/proyectos/resumen')
@login.login_required
def proyectos_resumen_view():
    """ Resumen de los proyectos de un alumno """

    form = LoginForm()
    proyectos = Proyecto.objects(alumnos=g.user.id).all()

    return render_template('proyectos_resumen.html',
        form = form,
        user = g.user,
        proyectos = proyectos)

@app.route('/tribunal/<proyecto>', methods = ('GET', 'POST'))
@login.login_required
def tribunal_view(proyecto):
    """ Inclusion de los datos de un tribunal """

    form = LoginForm()

    # obtener el proyecto que hemos referenciado
    proyecto = Proyecto.objects(id = proyecto).first()  

    # obtener todos los profesores. NOTA: No se consulta sobre Usuario !!!
    profesores = Profesor.objects().all() 

    if request.method == 'POST':
        # creo un diccionario con la informacion enviada al servidor
        d = {}
        d[request.form.get('profesor-0')] = request.form.get('rol-0')
        d[request.form.get('profesor-1')] = request.form.get('rol-1')
        d[request.form.get('profesor-2')] = request.form.get('rol-2')
        d[request.form.get('profesor-3')] = request.form.get('rol-3')
        d[request.form.get('profesor-4')] = request.form.get('rol-4')

        # creo un objeto tribunal que incluyo como documento embebido del proyecto
        t = Tribunal(miembros = d, comentarios = request.form.get('comentarios'))
        proyecto.tribunal = t

        # guardo y vuelvo a cargar para futuros usos
        proyecto.save()
        proyecto.reload()

        # feedback
        mensaje = 'Incluida la informacion del tribunal en el proyecto '
        flash(mensaje)

        return redirect(url_for('home_view', user = g.user))

    return render_template('tribunal.html',
        form = form,
        user = g.user,
        proyecto = proyecto,
        profesores = profesores,
        proyectos_totales = contar_proyectos())