from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Fechas(models.Model):
	agno = models.IntegerField(max_length=60)
	mes = models.IntegerField(max_length=60)
	nombre_mes = models.IntegerField(max_length=60)

	def __str__(self):
		return f"{self.agno}-{self.mes}"
class CustomUser(AbstractUser):
	''' Clase para la gestión de usuarios registrados en el sitio web '''
	# INFORMACIÓN PERSONAL
	email = models.EmailField('email', max_length=100)
	matricula = models.CharField('Matrícula', max_length=255, unique=True, null=True, blank=True)
	foto = models.ImageField('Foto', upload_to='fotos_usuarios/', max_length=255, null=True, blank=True)
	apell_pat = models.CharField('Apellido Paterno', max_length=100, null=True, blank=True)
	apell_mat = models.CharField('Apellido Materno', max_length=100, null=True, blank=True)
	ci = models.CharField('CI', max_length=50, unique=True)
	direcc = models.CharField('Dirección', max_length=200, null=True, blank=True)
	telefono = models.CharField('Teléfono', max_length=20, null=True, blank=True)
	celular = models.CharField('Celular', max_length=20, null=True, blank=True)
	fecha_registro = models.DateField('Fecha de matrícula ICAP', default=timezone.now())
	usuario_vivo = models.BooleanField('Vivo', default=True)  # Usuario vivo ó fallecido
	estado_usuario = models.BooleanField('Activo', default=True)

	# CAMPOS NUEVOS (22-03-21)
	lugar_nac = models.CharField('Lugar de nacimiento', max_length=200, null=True, blank=True)
	fecha_nac = models.DateField('Fecha de nacimiento', null=True, blank=True)
	est_civil = models.CharField('Estado civil', max_length=50, null=True, blank=True)
	univ_estud = models.CharField('Universidad de estudio', max_length=200, null=True, blank=True)
	fecha_tg = models.DateField('Fecha de Tesis o Grado', null=True, blank=True)
	univ_lic = models.CharField('Universidad que le otorgó la Licenciatura', max_length=200, null=True, blank=True)
	fecha_ol = models.DateField('Fecha en que se otorgó la Licenciatura', null=True, blank=True)
	fecha_tit_pn = models.DateField('Fecha título Provisión Nacional', null=True, blank=True)
	ent_pub = models.CharField('Entidad pública - privada', max_length=200, null=True, blank=True)
	cargos_judic = models.CharField('Cargos desemp. en el ramo judicial', max_length=200, null=True, blank=True)
	cargos_admin_pub = models.CharField('Cargos desemp. en la Administración Pública', max_length=200, null=True, blank=True)
	cargos_priv_otras = models.CharField('Cargos desemp. en empresas privadas u otras instituciones', max_length=200, null=True, blank=True)
	tiempo_ejec_prof_sd = models.CharField('Tiempo de ejecución profesional sin dependencia (BUFETE)', max_length=50, null=True, blank=True)
	cargo_actual = models.CharField('Cargo actual', max_length=50, null=True, blank=True)
	prod_jur = models.CharField('Producciones jurídicas', max_length=200, null=True, blank=True)
	estud_espec = models.CharField('Estudios de especialización', max_length=100, null=True, blank=True)
	recon_obt = models.CharField('Reconocimientos obtenidos', max_length=100, null=True, blank=True)
	asist_event_inter = models.CharField('Asistencia a eventos internacionales', max_length=100, null=True, blank=True)
	inst_aseg = models.CharField('Instituciones donde cuente con seguro', max_length=100, null=True, blank=True)
	beneficiarios = models.CharField('Beneficiarios', max_length=200, null=True, blank=True)
	espec_ejer_der = models.CharField('Especialidad en el ejercicio del Derecho', max_length=200, null=True, blank=True)
	direc_ofic = models.CharField('Dirección oficina', max_length=200, null=True, blank=True)
	tel_ofic = models.CharField('Teléfono de oficina', max_length=20, null=True, blank=True)
	observ = models.TextField('Observaciones', null=True, blank=True)
	# Nuevo campo Expedido
	expedido = models.CharField('Expedido',  max_length=200 , null=True, blank=True)

class RegistrarUsuario(models.Model):
	''' SOLO SE USARÁ PARA SOLVENTAR PROBLEMAS FUNCIONALES '''
	
	foto = models.ImageField('Foto', upload_to='fotos_usuarios/', max_length=255, null=True, blank=True)
	lugar_nac = models.CharField('Lugar de nacimiento', max_length=200, null=True, blank=True)
	fecha_nac = models.DateField('Fecha de nacimiento', null=True, blank=True)
	est_civil = models.CharField('Estado civil', max_length=50, null=True, blank=True)
	univ_estud = models.CharField('Universidad de estudio', max_length=200, null=True, blank=True)
	fecha_tg = models.DateField('Fecha de Tesis o Grado', null=True, blank=True)
	univ_lic = models.CharField('Universidad que le otorgó la Licenciatura', max_length=200, null=True, blank=True)
	fecha_ol = models.DateField('Fecha en que se otorgó la Licenciatura', null=True, blank=True)
	fecha_tit_pn = models.DateField('Fecha título Provición Nacional', null=True, blank=True)
	ent_pub = models.CharField('Entidad pública- Abogado', max_length=200, null=True, blank=True)
	cargos_judic = models.CharField('Cargos desemp. en el ramo judicial', max_length=200, null=True, blank=True)
	cargos_admin_pub = models.CharField('Cargos desemp. en la Administración Pública', max_length=200, null=True, blank=True)
	cargos_priv_otras = models.CharField('Cargos desemp. en empresas privadas u otras instituciones', max_length=200, null=True, blank=True)
	tiempo_ejec_prof_sd = models.CharField('Tiempo de ejecución profesional sin dependencia (BUFETE)', max_length=50, null=True, blank=True)
	cargo_actual = models.CharField('Cargo actual', max_length=50, null=True, blank=True)
	prod_jur = models.CharField('Producciones jurídicas', max_length=200, null=True, blank=True)
	estud_espec = models.CharField('Estudios de especialización', max_length=100, null=True, blank=True)
	recon_obt = models.CharField('Reconocimientos obtenidos', max_length=100, null=True, blank=True)
	asist_event_inter = models.CharField('Asistencia a eventos internacionales', max_length=100, null=True, blank=True)
	inst_aseg = models.CharField('Instituciones donde se haya asegurado', max_length=100, null=True, blank=True)
	beneficiarios = models.CharField('Beneficiarios', max_length=200, null=True, blank=True)
	espec_ejer_der = models.CharField('Especialidad en el ejercicio del Derecho', max_length=200, null=True, blank=True)
	direc_ofic = models.CharField('Dirección oficina', max_length=200, null=True, blank=True)
	tel_ofic = models.CharField('Teléfono de oficina', max_length=20, null=True, blank=True)
	direcc = models.CharField('Dirección', max_length=200, null=True, blank=True)
	telefono = models.CharField('Teléfono', max_length=20, null=True, blank=True)
	celular = models.CharField('Celular', max_length=20, null=True, blank=True)
	observ = models.TextField('Observaciones', null=True, blank=True)
	
	first_name = models.CharField('Nombre', max_length=50)
	apell_pat = models.CharField('Apellido (P)', max_length=50)
	apell_mat = models.CharField('Apellido (M)', max_length=50)
	matricula = models.CharField('Matrícula', max_length=255, unique=True, null=True, blank=True)
	ci = models.CharField('CI', max_length=30)
	email = models.EmailField('email', max_length=100)
	username = models.CharField('Username', max_length=100)
	usuario_vivo = models.BooleanField('Está vivo', default=True)
	estado_usuario = models.BooleanField('Está ACTIVO', default=True)
	password_new1 = models.CharField('NewPassword1', max_length=100, default='NuevaClave1')
	password_new2 = models.CharField('NewPassword2', max_length=100, default='NuevaClave2')
	password1 = models.CharField('Password1', max_length=100)
	password2 = models.CharField('Password2', max_length=100)
	fecha_registro = models.DateField('Fecha de registro personalizada', default=timezone.now())

	class Meta:
		verbose_name = 'CampoUsuario'
		verbose_name_plural = 'CamposUsuarios'

	def __str__(self):
		return self.username

class AporteMensual(models.Model):
	aporte_mensual_deno = models.CharField('Denominación', max_length=3, default='AMU', unique=True)
	aporte_mensual = models.CharField('Aporte Mensual (Bs)', max_length=50)
	fecha_inicio_cobros = models.DateField('Fecha de inicio de cobros mensuales', default=timezone.now())

	class Meta:
		verbose_name = 'aporte_mensual'
		verbose_name_plural = 'aportes_mensuales'

	def __str__(self):
		return self.aporte_mensual_deno

class AporteCertificacion(models.Model):
	aporte_certificacion = models.CharField('Aporte Certificación (Bs)', max_length=50)
	aporte_certificacion_deno = models.CharField('Nombre del certificado', max_length=20, default='CERTIFICADO', unique=True)

	class Meta:
		verbose_name = 'aporte_certificación'
		verbose_name_plural = 'aportes_certificación'

	def __str__(self):
		return self.aporte_certificacion_deno

class AporteAfiliado(models.Model):
	afiliado = models.ForeignKey(settings.AUTH_USER_MODEL,
					limit_choices_to={'groups__name': 'Afiliado'},
					on_delete=models.CASCADE)
	
	recaudador = models.ForeignKey(
					settings.AUTH_USER_MODEL,
					limit_choices_to={'groups__name': 'Recaudador'},
					related_name='aporte_recaudador',
					null=True,
					blank=True,
					on_delete=models.CASCADE)
	
	aporte_mensual_afil = models.ForeignKey(AporteMensual, on_delete=models.CASCADE, null=True, blank=True)
	aporte_certif_afil = models.ForeignKey(AporteCertificacion, on_delete=models.CASCADE, null=True, blank=True)
	aporte_dona_afil = models.CharField('Aporte por donación', max_length=50, default=0)
	fecha_pago = models.DateField('Fecha de pago', default=timezone.now())
	comprobante = models.CharField('Comprobante de transacción', max_length=6, unique=True, default=000000)
	talonario = models.CharField('Talonario de cobro', max_length=8)
	fecha_id_pago = models.ForeignKey(Fechas, on_delete=models.CASCADE, null=True, blank=True)
	numero_recibo = models.CharField('Numero de recibo', max_length=5,null=True,blank=True)

	class Meta:
		verbose_name = 'aporte_afiliado'
		verbose_name_plural = 'aportes_afiliado'

	def __str__(self):
		return self.comprobante
