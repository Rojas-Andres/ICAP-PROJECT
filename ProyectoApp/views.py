# DJANGO
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import FormView
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.template.loader import get_template
from datetime import datetime
#from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta
import random
# MÓDULOS EXTERNOS
import io
from datetime import date
from dateutil import rrule

# PROPIOS DEL PROYECTO
from .forms import FormularioLogin, FormularioRegistroUsuario, FormularioModificarDatos, FormularioModificarClave
from .forms import FormularioFiltrarUsuarioCI, FormularioFiltrarUsuarioMAT
from .forms import FormularioCobrarAM, FormularioCobrarAC, FormularioCobrarAD, FormularioCobroMult
from .forms import FormularioModificarUsuario, FormularioSubirFoto, FormularioFechas
from .forms import FormularioActualizarDatos, FormularioFiltrarUsuarioApellPat
from .forms import FormularioFiltrarComprobante, FormularioFiltrarTalonario
from .forms import FormularioRegistrarCobro, FormularioYear, FormularioRegistroAfiliadoAntiguo
from .models import CustomUser, AporteAfiliado, AporteMensual, AporteCertificacion,Fechas
from .tasks import *  # TAREAS VARIADAS PARA LA EJECUCIÓN Y/O HERRAMIENTAS

# -------------------------------- VISTAS GENERALES ----------------------------------------------------

class Login(FormView):
	''' Acceso para los usuarios (Directivo, Recaudador y Afiliado) (font-end) '''
	template_name = 'ProyectoApp/login.html'
	form_class = FormularioLogin
	success_url = reverse_lazy('check-user')

	@method_decorator(csrf_protect)
	@method_decorator(never_cache)
	def dispatch(self, request, *args, **kwargs):
		print("pase por aqui")
		print(request)
		if request.user.is_authenticated:
			return HttpResponseRedirect(self.get_success_url())
		else:
			return super(Login, self).dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		print("pase por aqui")
		print(form.get_user())
		login(self.request, form.get_user())
		return super(Login, self).form_valid(form)

def logout_usuario(request):
	''' Cerrar sesión y volver al index del sitio web '''
	logout(request)
	return redirect('inicio')

class ComprobarUsuario(View):
	''' Vista que verifica cuál rol de usuario está ingresando '''
	def get(self, request, *args, **kwargs):

		if str(request.user.groups.get()) == 'Directivo':
			return redirect('directivo-bienvenida')
		
		elif str(request.user.groups.get()) == 'Recaudador':
			return redirect('recaudador-bienvenida')
		
		elif str(request.user.groups.get()) == 'Afiliado':
			return redirect('afiliado-bienvenida')
		
		else:
			return redirect('inicio')

class Inicio(ListView):
	''' Index o vista inicial del sitio web '''
	def get(self, request, *args, **kwargs):
		context = {}
		return render(request, 'ProyectoApp/index.html', context)

# --------------------------------------- VISTAS PARA LOS DIRECTIVOS -------------------------------------------
class DirectivoBienvenida(ListView):
	''' Ventana de bienvenida cada vez que un Directivo ingresa al sitio web '''
	def get(self, request, *args, **kwargs):

		if request.user.groups.filter(name__in=['Directivo']):

			user_log = CustomUser.objects.get(username=request.user)
			
			context = {
				'user_log': user_log
			}

			return render(request, 'ProyectoApp/directivo/directivo-bienvenida.html', context)

		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoDashboard(DetailView):
	''' Información relacionada a su rol de Directivo '''
	def get(self, request, user_log, *args, **kwargs):

		if request.user.groups.filter(name__in=['Directivo']):

			context = generar_info_direc(request, user_log)  # Carga toda su información
			
			return render(request, 'ProyectoApp/directivo/directivo-dashboard.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoVerMiKardex(DetailView):
	def get(self, request, user_log, *args, **kwargs):

		if request.user.groups.filter(name__in=['Directivo']):

			context = {
				'user_log': CustomUser.objects.get(username=user_log)
			}
			
			return render(request, 'ProyectoApp/directivo/directivo-ver-mi-kardex.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoDashboardAfiliados(DetailView):
	''' Información relacionada a su rol de Directivo '''
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			context = generar_info_direc_afiliados(request, user_log)
			
			return render(request, 'ProyectoApp/directivo/directivo-dashboard-afiliados.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoDashboardAfiliadosDesh(DetailView):
	''' Filtrar los afiliados deshabilitados por el sistema '''
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			context = generar_info_direc_afiliados_desh(request, user_log)
			
			return render(request, 'ProyectoApp/directivo/directivo-dashboard-afiliados-desh.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoDashboardAfiliadosDeudas(DetailView):
	''' Filtrar a los afiliados que presenten deudas '''
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			
			afiliados_deudas = generar_info_direc_afiliados_deudas(request, user_log)
			
			fact_emit_total = 0
			fact_paga_total = 0
			fact_venc_total = 0
			deuda_total = 0

			for afiliado in afiliados_deudas:
				fact_emit_total += afiliado['fact_emitidas']

			for afiliado in afiliados_deudas:
				fact_paga_total += afiliado['fact_pagadas']

			for afiliado in afiliados_deudas:
				fact_venc_total += afiliado['fact_vencidas']

			for afiliado in afiliados_deudas:
				deuda_total += afiliado['deuda']

			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'afiliados_deudas': afiliados_deudas,
				'fact_emit_total': fact_emit_total,
				'fact_paga_total': fact_paga_total,
				'fact_venc_total': fact_venc_total,
				'deuda_total': deuda_total

			}

			#return HttpResponse(f'{context}')
			return render(request, 'ProyectoApp/directivo/directivo-dashboard-afiliados-deudas.html', context)
		
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoRegistroRecaudador(DetailView):
	''' Registro de afiliados (Font-end) '''
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			print("HOLA ENTRE DESDE EL RECAUDADOR")
			form = FormularioRegistroUsuario()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/directivo/directivo-registrar.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioRegistroUsuario(request.POST, request.FILES)
			if form.is_valid():
				if form.cleaned_data['password1'] == form.cleaned_data['password2']:
					try:
						
						user_new = CustomUser.objects.create_user(
							first_name=form.cleaned_data['first_name'].upper(),
							apell_pat=form.cleaned_data['apell_pat'].upper(),
							apell_mat=form.cleaned_data['apell_mat'].upper(),
							username=form.cleaned_data['username'],
							password=form.cleaned_data['password1'],
							email=form.cleaned_data['email'],
							matricula=str(random.getrandbits(128)),
							ci=form.cleaned_data['ci'],
							fecha_registro=form.cleaned_data['fecha_registro'],
							foto = form.cleaned_data['foto'],
							# usuario_vivo = form.cleaned_data['usuario_vivo'],
							# estado_usuario = form.cleaned_data['estado_usuario'],
							lugar_nac = form.cleaned_data['lugar_nac'],
							fecha_nac = form.cleaned_data['fecha_nac'],
							est_civil = form.cleaned_data['est_civil'],
							univ_estud = form.cleaned_data['univ_estud'],
							fecha_tg = form.cleaned_data['fecha_tg'],
							univ_lic = form.cleaned_data['univ_lic'],
							fecha_ol = form.cleaned_data['fecha_ol'],
							ent_pub = form.cleaned_data['ent_pub'],
							fecha_tit_pn = form.cleaned_data['fecha_tit_pn'],
							cargos_judic = form.cleaned_data['cargos_judic'],
							cargos_admin_pub = form.cleaned_data['cargos_admin_pub'],
							cargos_priv_otras = form.cleaned_data['cargos_priv_otras'],
							tiempo_ejec_prof_sd = form.cleaned_data['tiempo_ejec_prof_sd'],
							cargo_actual = form.cleaned_data['cargo_actual'],
							prod_jur = form.cleaned_data['prod_jur'],
							estud_espec = form.cleaned_data['estud_espec'],
							recon_obt = form.cleaned_data['recon_obt'],
							asist_event_inter = form.cleaned_data['asist_event_inter'],
							inst_aseg = form.cleaned_data['inst_aseg'],
							beneficiarios = form.cleaned_data['beneficiarios'],
							espec_ejer_der = form.cleaned_data['espec_ejer_der'],
							direc_ofic = form.cleaned_data['direc_ofic'],
							tel_ofic = form.cleaned_data['tel_ofic'],
							direcc = form.cleaned_data['direcc'],
							telefono = form.cleaned_data['telefono'],
							celular = form.cleaned_data['celular'],
							observ = form.cleaned_data['observ'],
							expedido = form.cleaned_data['expedido'],
							)

						user_new.groups.add(Group.objects.get(name='Recaudador'))
						user_new.save()
						
						user_new = CustomUser.objects.get(username=form.cleaned_data['username'])
						user_new.foto = form.cleaned_data['foto']
						user_new.save()

						messages.success(request, '¡Recaudador creado correctamente!')

						return HttpResponseRedirect(f'/directivo{user_log}/')
					
					except Exception as e:
						if str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.matricula':
							messages.error(
								request, f'Ya existe un colegiado con esa matrícula')
							return HttpResponseRedirect(f'/direcregistrec{user_log}/')
						
						elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.ci':
							messages.error(
								request, f'Ya existe un colegiado con ese C.I')
							return HttpResponseRedirect(f'/direcregistrec{user_log}/')
						
						elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.username':
							
							messages.error(request, 'Ya existe un colegiado con ese username')
							return HttpResponseRedirect(f'/direcregistrec{user_log}/')

						else:
							print(e)
							messages.error(request, f'¡Valor incorrecto en datos!')
							return HttpResponseRedirect(f'/direcregistrec{user_log}/')
		
				else:
					messages.error(request, 'Las contraseñas no coinciden')
					return HttpResponseRedirect(f'/direcregistrec{user_log}/')
				
			else:
				messages.error(request, 'La matrícula no puede tener más de 4 dígitos')
				return HttpResponseRedirect(f'/direcregistrec{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoTipoAfiliado(DetailView):
	''' Elegir si el afiliado es totalmente nuevo o si 
	proviene del anterior sistemas '''
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):

			context = {
				'user_log': CustomUser.objects.get(username=user_log)
			}

			return render(request, 'ProyectoApp/directivo/directivo-tipo-afiliado.html', context)

		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')


def validate_number(matricula):
	matricula_formulario = CustomUser.objects.filter(matricula = matricula).first()
	if(matricula_formulario):
		return False
	else:
		return True


class DirectivoRegistroAfiliado(DetailView):
	''' Registro de afiliados (Font-end) '''
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioRegistroUsuario()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form,
				'afiliado': True
				}
			return render(request, 'ProyectoApp/directivo/directivo-registrar.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioRegistroUsuario(request.POST, request.FILES)
			if not validar_matricula(str(request.POST["matricula"])):
				messages.error(request, 'La matrícula no puede estar vacia y no puede exceder los 4 digitos')
				return HttpResponseRedirect(f'/rehasdamaafilant{user_log}/')
			if form.is_valid():
				
				if form.cleaned_data['password1'] == form.cleaned_data['password2']:
					
					try:
						user_new = CustomUser.objects.create_user(
							first_name=form.cleaned_data['first_name'].upper(),
							apell_pat=form.cleaned_data['apell_pat'].upper(),
							apell_mat=form.cleaned_data['apell_mat'].upper(),
							username=form.cleaned_data['username'],
							password=form.cleaned_data['password1'],
							email=form.cleaned_data['email'],
							matricula=form.cleaned_data['matricula'],
							ci=form.cleaned_data['ci'],
							fecha_registro=form.cleaned_data['fecha_registro'],
							
							foto = form.cleaned_data['foto'],
							usuario_vivo = True,
							estado_usuario = form.cleaned_data['estado_usuario'],
							lugar_nac = form.cleaned_data['lugar_nac'],
							fecha_nac = form.cleaned_data['fecha_nac'],
							est_civil = form.cleaned_data['est_civil'],
							univ_estud = form.cleaned_data['univ_estud'],
							fecha_tg = form.cleaned_data['fecha_tg'],
							univ_lic = form.cleaned_data['univ_lic'],
							fecha_ol = form.cleaned_data['fecha_ol'],
							ent_pub = form.cleaned_data['ent_pub'],
							fecha_tit_pn = form.cleaned_data['fecha_tit_pn'],
							cargos_judic = form.cleaned_data['cargos_judic'],
							cargos_admin_pub = form.cleaned_data['cargos_admin_pub'],
							cargos_priv_otras = form.cleaned_data['cargos_priv_otras'],
							tiempo_ejec_prof_sd = form.cleaned_data['tiempo_ejec_prof_sd'],
							cargo_actual = form.cleaned_data['cargo_actual'],
							prod_jur = form.cleaned_data['prod_jur'],
							estud_espec = form.cleaned_data['estud_espec'],
							recon_obt = form.cleaned_data['recon_obt'],
							asist_event_inter = form.cleaned_data['asist_event_inter'],
							inst_aseg = form.cleaned_data['inst_aseg'],
							beneficiarios = form.cleaned_data['beneficiarios'],
							espec_ejer_der = form.cleaned_data['espec_ejer_der'],
							direc_ofic = form.cleaned_data['direc_ofic'],
							tel_ofic = form.cleaned_data['tel_ofic'],
							direcc = form.cleaned_data['direcc'],
							telefono = form.cleaned_data['telefono'],
							celular = form.cleaned_data['celular'],
							observ = form.cleaned_data['observ'],
							expedido = form.cleaned_data['expedido'],
							)

						user_new.groups.add(Group.objects.get(name='Afiliado'))
						user_new.save()
						
						messages.success(request, '¡Afiliado creado correctamente!')
						return HttpResponseRedirect(f'/directivo{user_log}/afiliados/')
						
					except Exception as e:
						if str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.matricula':
							messages.error(
								request, f'Ya existe un colegiado con esa matrícula')
							return HttpResponseRedirect(f'/direcregistafil{user_log}/')
						
						elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.ci':
							messages.error(
								request, f'Ya existe un colegiado con ese C.I')
							return HttpResponseRedirect(f'/direcregistafil{user_log}/')
						
						elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.username':
							
							messages.error(request, 'Ya existe un colegiado con ese username')
							return HttpResponseRedirect(f'/direcregistafil{user_log}/')
						else:
							messages.error(request, f'¡Error en datos datos!')
							return HttpResponseRedirect(f'/direcregistafil{user_log}/')
				
				else:
					messages.error(request, 'Las contraseñas no coinciden')
					return HttpResponseRedirect(f'/direcregistafil{user_log}/')
				
			else:
				messages.error(request, 'La matrícula no puede tener más de 4 dígitos')
				return HttpResponseRedirect(f'/direcregistafil{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoRegistroAfiliadoAntiguo(DetailView):
	''' Registro de afiliados (Font-end) '''
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			print("HOLA ENTRE desde el afi")
			form = FormularioRegistroAfiliadoAntiguo()

			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form,
				'afiliado': True
				}
			return render(request, 'ProyectoApp/directivo/directivo-registrar-afil-ant.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
    
		if request.user.groups.filter(name__in=['Directivo']):
		
			form = FormularioRegistroAfiliadoAntiguo(request.POST, request.FILES)
			if not validar_matricula(str(request.POST["matricula"])):
				messages.error(request, 'La matrícula no puede estar vacia y no puede exceder los 4 digitos')
				return HttpResponseRedirect(f'/rehasdamaafilant{user_log}/')
			if form.is_valid():	
				if form.cleaned_data['password1'] == form.cleaned_data['password2']:	
					print("\n\n\n")
					print(form.data["expedido"])	
					try:
						user_new = CustomUser.objects.create_user(
							first_name=form.cleaned_data['first_name'].upper(),
							apell_pat=form.cleaned_data['apell_pat'].upper(),
							apell_mat=form.cleaned_data['apell_mat'].upper(),
							username=form.cleaned_data['username'],
							password=form.cleaned_data['password1'],
							email=form.cleaned_data['email'],
							matricula=form.cleaned_data['matricula'],
							ci=form.cleaned_data['ci'],
							fecha_registro=form.cleaned_data['fecha_registro'],
							foto = form.cleaned_data['foto'],
							usuario_vivo = form.cleaned_data['usuario_vivo'],
							estado_usuario = form.cleaned_data['estado_usuario'],
							lugar_nac = form.cleaned_data['lugar_nac'],
							fecha_nac = form.cleaned_data['fecha_nac'],
							est_civil = form.cleaned_data['est_civil'],
							univ_estud = form.cleaned_data['univ_estud'],
							fecha_tg = form.cleaned_data['fecha_tg'],
							univ_lic = form.cleaned_data['univ_lic'],
							fecha_ol = form.cleaned_data['fecha_ol'],
							ent_pub = form.cleaned_data['ent_pub'],
							fecha_tit_pn = form.cleaned_data['fecha_tit_pn'],
							cargos_judic = form.cleaned_data['cargos_judic'],
							cargos_admin_pub = form.cleaned_data['cargos_admin_pub'],
							cargos_priv_otras = form.cleaned_data['cargos_priv_otras'],
							tiempo_ejec_prof_sd = form.cleaned_data['tiempo_ejec_prof_sd'],
							cargo_actual = form.cleaned_data['cargo_actual'],
							prod_jur = form.cleaned_data['prod_jur'],
							estud_espec = form.cleaned_data['estud_espec'],
							recon_obt = form.cleaned_data['recon_obt'],
							asist_event_inter = form.cleaned_data['asist_event_inter'],
							inst_aseg = form.cleaned_data['inst_aseg'],
							beneficiarios = form.cleaned_data['beneficiarios'],
							espec_ejer_der = form.cleaned_data['espec_ejer_der'],
							direc_ofic = form.cleaned_data['direc_ofic'],
							tel_ofic = form.cleaned_data['tel_ofic'],
							direcc = form.cleaned_data['direcc'],
							telefono = form.cleaned_data['telefono'],
							celular = form.cleaned_data['celular'],
							observ = form.cleaned_data['observ'],
							expedido = form.cleaned_data['expedido'],
							)

						user_new.groups.add(Group.objects.get(name='Afiliado'))
						user_new.save()
						
						try:
							# CARGAR LOS APORTES MENSUALES DEL ANTERIOR SISTEMA
							cargar_aportes = cobrar_aporte_mult(
								request, user_log, form.cleaned_data['username'],
								form.cleaned_data['fecha_registro'], int(form.cleaned_data['cant_aportes_iniciales']),
								'AMI', form.cleaned_data['talonario'])

							print('SE PUDOOOOOOOOOOOOOOOO')

						except Exception as e:
							print('NO SE PUDOOOOOOOOO')
							print(e)

						messages.success(request, '¡Afiliado creado correctamente!')
						return HttpResponseRedirect(f'/directivo{user_log}/afiliados/')
						
					except Exception as e:
						

						if str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.matricula':
							messages.error(
								request, f'Ya existe un colegiado con esa matrícula')
							return HttpResponseRedirect(f'/dihashdaskantg{user_log}/')
						
						elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.ci':
							messages.error(
								request, f'Ya existe un colegiado con ese C.I')
							return HttpResponseRedirect(f'/dihashdaskantg{user_log}/')
						
						elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.username':
							
							messages.error(request, 'Ya existe un colegiado con ese username')
							return HttpResponseRedirect(f'/dihashdaskantg{user_log}/')
						else:
							messages.error(request, f'¡Error en datos datos!')
							return HttpResponseRedirect(f'/dihashdaskantg{user_log}/')
				
				else:
					messages.error(request, 'Las contraseñas no coinciden')
					return HttpResponseRedirect(f'/dihashdaskantg{user_log}/')
				
			else:
    			
				messages.error(request, 'La matrícula no puede tener más de 4 dígitos')
				print (form.errors)
				print(form.data["first_name"])
				return HttpResponseRedirect(f'/dihashdaskantg{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoFiltrarUsuarioCI(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioFiltrarUsuarioCI()
			
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/directivo/directivo-filtrar-ci.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioFiltrarUsuarioCI(request.POST)

			if form.is_valid():
				ci = form.cleaned_data['ci']

				try:
					user_get = CustomUser.objects.get(ci=ci)
					user_filt = user_get.username
				except:
					messages.info(request, f'No existe un usuario con C.I.:{ci}')
					return HttpResponseRedirect(f'/directivfdsfofiltci{user_log}')

				return HttpResponseRedirect(f'/directivofilt/{user_log}/{user_filt}/')
											
			else:
				messages.error(request, 'Datos introducidos incorrectamente')
				return HttpResponseRedirect(f'/directivfdsfofiltci{user_log}')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoFiltrarUsuarioMAT(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioFiltrarUsuarioMAT()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/directivo/directivo-filtrar-mat.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioFiltrarUsuarioMAT(request.POST)

			if form.is_valid():
				mat = form.cleaned_data['matricula']

				try:
					user_get = CustomUser.objects.get(matricula=mat)
					user_filt = user_get.username
				except:
					messages.info(request, f'No existe un usuario con matrícula:{mat}')
					return HttpResponseRedirect(f'/directsfsfsivofiltmat{user_log}')

				return HttpResponseRedirect(f'/directivofilt/{user_log}/{user_filt}/')
											
			else:
				messages.error(request, 'Máximo 4 dígitos')
				return HttpResponseRedirect(f'/directsfsfsivofiltmat{user_log}')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoFiltrarUsuarioApellPat(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioFiltrarUsuarioApellPat()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/directivo/directivo-filtrar-apell-pat.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioFiltrarUsuarioApellPat(request.POST)

			if form.is_valid():
				apell_pat = form.cleaned_data['apell_pat']

				try:
					user_log = CustomUser.objects.get(username=user_log)
					user_filts = CustomUser.objects.filter(apell_pat__iexact=apell_pat)

					

					if len(user_filts) == 0:
						messages.info(request, f'No existe un usuario con apellido paterno: {apell_pat}')
						return HttpResponseRedirect(f'/directsfsfsivofiltapellpat{user_log}')

					else:
						context = {
							'user_log': user_log,
							'user_filts': user_filts
						}

						return render(
							request, 
							'ProyectoApp/directivo/directivo-dashboard-filtrado-apell-pat.html',
							context
						)

				except:
					messages.info(request, f'No existe un usuario con apellido paterno: {apell_pat}')
					return HttpResponseRedirect(f'/directsfsfsivofiltapellpat{user_log}')

				return HttpResponseRedirect(f'/directivofilt/{user_log}/{user_filt}/')
											
			else:
				messages.error(request, 'Sólo letras')
				return HttpResponseRedirect(f'/directsfsfsivofiltapellpat{user_log}')
		else:
			return HttpResponse('No tienes permiso para acceder a este usuario')

class DirectivoDashboardFiltrado(DetailView):
	def get(self, request, user_log, user_filt, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			check_afil = CustomUser.objects.get(username=user_filt)
			if not check_afil.groups.filter(name__in=['Directivo']):
				context = filtrar_info(request, user_log, user_filt)
				
				return render(request, 'ProyectoApp/directivo/directivo-dashboard-filtrado.html', context)
			else:
				return HttpResponse('No tienes permiso para acceder a este usuario')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoFiltrarComprobante(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioFiltrarComprobante()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/directivo/directivo-filtrar-comp.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioFiltrarComprobante(request.POST)

			if form.is_valid():
				comp = form.cleaned_data['comprobante']

				try:
					
					user_log = CustomUser.objects.get(username=user_log)
					aporte = AporteAfiliado.objects.get(comprobante=comp)
					recaudador = CustomUser.objects.get(username=aporte.recaudador)
					afiliado = CustomUser.objects.get(username=aporte.afiliado)
					
					context = {
						'user_log': user_log,
						'comprobante': comp,
						'aporte': aporte,
						'recaudador': recaudador,
						'afiliado': afiliado
					}
					
					return render(request, 'ProyectoApp/directivo/directivo-dashboard-comprobante.html', context)
				except:
					messages.info(request, f'No existe un aporte mensual con comprobante = {comp}')
					return HttpResponseRedirect(f'/directsfsfsivofiltcomp{user_log}/')
			else:
				messages.error(request, 'Debe tener seis (06) dígitos')
				return HttpResponseRedirect(f'/directsfsfsivofiltcomp{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoFiltrarTalonario(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioFiltrarTalonario()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/directivo/directivo-filtrar-talon.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioFiltrarTalonario(request.POST)

			if form.is_valid():
				talon = form.cleaned_data['talonario']

				try:
					
					user_log = CustomUser.objects.get(username=user_log)
					aportes = AporteAfiliado.objects.filter(talonario__icontains=talon)
					
					paginator = Paginator(aportes, 15)  # Mostrará hasta 15 aportes por pág.
					page = request.GET.get('page')
					aportes = paginator.get_page(page)

					context = {
						'user_log': user_log,
						'talonario': talon,
						'aportes': aportes,
					}

					return render(request, 'ProyectoApp/directivo/directivo-dashboard-talonario.html', context)
				except:
					messages.info(request, f'No existe un aporte mensual con talonario = {talon}')
					return HttpResponseRedirect(f'/directsfsfsivofilttalon{user_log}/')
			else:
				messages.error(request, 'Debe tener seis (06) dígitos')
				return HttpResponseRedirect(f'/directsfsfsivofilttalon{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoDetalles(DetailView):
	def get(self, request, user_log, comprobante, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			
			user_log = CustomUser.objects.get(username=user_log)
			info = AporteAfiliado.objects.get(comprobante=comprobante)

			context = {
				'user_log': user_log,
				'info': info
			}

			return render(request, 'ProyectoApp/directivo/directivo-detalles.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoModDatos(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			
			user_log = CustomUser.objects.get(username=user_log)

			form = FormularioModificarDatos(
				initial={
				'ci': user_log.ci,
				'email': user_log.email,
				'first_name': user_log.first_name, 
				'apell_pat': user_log.apell_pat,
				'apell_mat': user_log.apell_mat,
				'telefono': user_log.telefono,
				'celular': user_log.celular,
				'direcc': user_log.direcc,			
				'lugar_nac': user_log.lugar_nac,
				'fecha_nac': user_log.fecha_nac,
				'est_civil': user_log.est_civil,
				'univ_estud': user_log.univ_estud,
				'fecha_tg': user_log.fecha_tg,
				'univ_lic': user_log.univ_lic,
				'fecha_ol': user_log.fecha_ol,
				'ent_pub': user_log.ent_pub,
				'fecha_tit_pn': user_log.fecha_tit_pn,
				'cargos_judic': user_log.cargos_judic,
				'cargos_admin_pub': user_log.cargos_admin_pub,
				'cargos_priv_otras': user_log.cargos_priv_otras,
				'tiempo_ejec_prof_sd': user_log.tiempo_ejec_prof_sd,
				'cargo_actual': user_log.cargo_actual,
				'prod_jur': user_log.prod_jur,
				'estud_espec': user_log.estud_espec,
				'recon_obt': user_log.recon_obt,
				'asist_event_inter': user_log.asist_event_inter,
				'inst_aseg': user_log.inst_aseg,
				'beneficiarios': user_log.beneficiarios,
				'espec_ejer_der': user_log.espec_ejer_der,
				'direc_ofic': user_log.direc_ofic,
				'tel_ofic': user_log.tel_ofic,
				}
			)
			
			context = {
				'user_log': user_log,
				'form': form
				}
			
			return render(request, 'ProyectoApp/directivo/directivo-mod-datos.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioModificarDatos(request.POST)

			if form.is_valid():
			
				try:	
					# Datos a cambiar
					user_mod = CustomUser.objects.get(username=user_log)
					
					user_mod.first_name = form.cleaned_data['first_name'].upper()
					user_mod.apell_pat = form.cleaned_data['apell_pat'].upper()
					user_mod.apell_mat = form.cleaned_data['apell_mat'].upper()
					user_mod.lugar_nac = form.cleaned_data['lugar_nac']
					user_mod.fecha_nac = form.cleaned_data['fecha_nac']
					user_mod.ci = form.cleaned_data['ci']
					user_mod.est_civil = form.cleaned_data['est_civil']
					user_mod.univ_estud = form.cleaned_data['univ_estud']
					user_mod.fecha_tg = form.cleaned_data['fecha_tg']
					user_mod.univ_lic = form.cleaned_data['univ_lic']
					user_mod.fecha_ol = form.cleaned_data['fecha_ol']
					user_mod.ent_pub = form.cleaned_data['ent_pub']
					user_mod.fecha_tit_pn = form.cleaned_data['fecha_tit_pn']
					user_mod.cargos_judic = form.cleaned_data['cargos_judic']
					user_mod.cargos_admin_pub = form.cleaned_data['cargos_admin_pub']
					user_mod.cargos_priv_otras = form.cleaned_data['cargos_priv_otras']
					user_mod.tiempo_ejec_prof_sd = form.cleaned_data['tiempo_ejec_prof_sd']
					user_mod.cargo_actual = form.cleaned_data['cargo_actual']
					user_mod.prod_jur = form.cleaned_data['prod_jur']
					user_mod.estud_espec = form.cleaned_data['estud_espec']
					user_mod.recon_obt = form.cleaned_data['recon_obt']
					user_mod.asist_event_inter = form.cleaned_data['asist_event_inter']
					user_mod.inst_aseg = form.cleaned_data['inst_aseg']
					user_mod.beneficiarios = form.cleaned_data['beneficiarios']
					user_mod.espec_ejer_der = form.cleaned_data['espec_ejer_der']
					user_mod.direc_ofic = form.cleaned_data['direc_ofic']
					user_mod.tel_ofic = form.cleaned_data['tel_ofic']
					user_mod.direcc = form.cleaned_data['direcc']
					user_mod.telefono = form.cleaned_data['telefono']
					user_mod.celular = form.cleaned_data['celular']
					user_mod.email = form.cleaned_data['email']

					user_mod.save()
					
					messages.success(request, '¡Datos modificados correctamente!')
					return HttpResponseRedirect(f'/directivo{user_log}/')

				except Exception as e:
					if str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.matricula':
						messages.error(
							request, f'Ya existe un colegiado con esa matrícula')
						return HttpResponseRedirect(f'/direcmoddatos/{user_log}/')
						
					elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.ci':
						messages.error(
							request, f'Ya existe un colegiado con ese C.I')
						return HttpResponseRedirect(f'/direcmoddatos/{user_log}/')
					
					elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.username':
							
							messages.error(request, 'Ya existe un colegiado con ese username')
							return HttpResponseRedirect(f'/direcmoddatos/{user_log}/')
						
					else:
						messages.error(request, 'Error en datos')
						return HttpResponseRedirect(f'/direcmoddatos/{user_log}/')

			else:
				messages.error(request, 'Datos incorrectos')
				return HttpResponseRedirect(f'/direcmoddatos/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoModClave(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioModificarClave()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/directivo/directivo-mod-clave.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioModificarClave(request.POST)

			if form.is_valid():
				
				if form.cleaned_data['password1'] == form.cleaned_data['password2']:
					
					directivo = CustomUser.objects.get(username=user_log)
					
					if directivo.check_password(form.cleaned_data['password1']):
						
						if form.cleaned_data['password_new1'] == form.cleaned_data['password_new2']:
					
							directivo.password = make_password(
										form.cleaned_data['password_new1'],
										salt=None,
										hasher='default'
									)
								
							directivo.save()

							messages.success(request, '¡Clave modificada correctamente!')
							return HttpResponseRedirect(f'/directivo{user_log}/')

						else:
							messages.error(request, 'Las claves no coinciden')
							return HttpResponseRedirect(f'/direcmodclave/{user_log}/')

					else:
						messages.error(request, 'Error en verificación de tu clave actual. No habrá cambios')
						return HttpResponseRedirect(f'/direcmodclave/{user_log}/')

				else:
					messages.error(request, 'Las claves actuales no coinciden')
					return HttpResponseRedirect(f'/direcmodclave/{user_log}/')

			else:
				messages.error(request, 'Datos introducidos incorrectamente')
				return HttpResponseRedirect(f'/direcmodclave/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoModFoto(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioSubirFoto()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/directivo/directivo-mod-foto.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioSubirFoto(request.POST, request.FILES)

			if form.is_valid():
		
				user_mod = CustomUser.objects.get(username=user_log)
				user_mod.foto = form.cleaned_data['foto']
				user_mod.save()

				messages.success(request, 'Foto actualizada')
				return HttpResponseRedirect(f'/directivo{user_log}/')
											
			else:
				messages.error(request, 'No se ha podido actualizar tu foto')
				return HttpResponseRedirect(f'/direcmodfoto/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoVerUsuario(DetailView):
	def get(self, request, user_log, usuario, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			
			context = directivo_ver_usuario(request, user_log, usuario)

			return render(request, 'ProyectoApp/directivo/directivo-ver-usuario.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoHistorialRecaudador(DetailView):
	def get(self, request, user_log, recaudador, tam, th, start_date, end_date, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			
			if th == 'TOTAL':
				context = historial_recaud(request, user_log, recaudador, tam, th)

			elif th == 'MES':
				context = historial_recaud_mes(request, user_log, recaudador, tam, th)

			else:
				context = historial_recaud_fechas(request, user_log, recaudador, tam, th, start_date, end_date)

			return render(request, 'ProyectoApp/directivo/directivo-historial-recaudador.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoHistorialAfiliado(DetailView):
	def get(self, request, user_log, afiliado, tam, th, start_date, end_date, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			
			if th == 'TOTAL':
				context = historial_afil(request, user_log, afiliado, tam, th)

			elif th == 'MES':
				context = historial_afil_mes(request, user_log, afiliado, tam, th)

			else:
				context = historial_afil_fechas(request, user_log, afiliado, tam, th, start_date, end_date)

			return render(request, 'ProyectoApp/directivo/directivo-historial-afiliado.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class ModificarUsuario(DetailView):
	def get(self, request, user_log, usuario, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo', 'Recaudador']):
			
			user_log = CustomUser.objects.get(username=user_log)
			usuario = CustomUser.objects.get(username=usuario)

			form = FormularioModificarUsuario(
				initial={
				'matricula': usuario.matricula,
				'ci': usuario.ci,
				'fecha_registro': usuario.fecha_registro,
				'email': usuario.email,
				'username': usuario.username,
				'usuario_vivo': True,
				}
			)

			if usuario.groups.filter(name__in=['Afiliado']):
				afiliado = True
			else:
				afiliado = False

			context = {
				'user_log': user_log,
				'form': form,
				'afiliado': afiliado
				}
			
			if user_log.groups.filter(name__in=['Directivo']):
				return render(request, 'ProyectoApp/directivo/directivo-mod-usuario.html', context)
			
			else:
				return render(request, 'ProyectoApp/recaudador/recaudador-mod-usuario.html', context)

		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, usuario, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo', 'Recaudador']):
			user_log = CustomUser.objects.get(username=user_log)
			form = FormularioModificarUsuario(request.POST)
			if not validar_matricula(str(request.POST["matricula"])):
				messages.error(request, 'La matrícula no puede estar vacia y no puede exceder los 4 digitos')
				return HttpResponseRedirect(f'/rehasdamaafilant{user_log}/')
			if form.is_valid():
					
				user_mod = CustomUser.objects.get(username=usuario)
				nuevo_username = form.cleaned_data['username']
				
				user_mod.username = nuevo_username
				user_mod.matricula = form.cleaned_data['matricula']
				user_mod.ci = form.cleaned_data['ci']
				user_mod.email = form.cleaned_data['email']
				user_mod.fecha_registro = form.cleaned_data['fecha_registro']
				user_mod.usuario_vivo = form.cleaned_data['usuario_vivo']
				user_mod.password = make_password(
									form.cleaned_data['password1'],
									salt=None,
									hasher='default'
								)
				user_mod.save()		
				
				
				
				if user_log.groups.filter(name__in=['Directivo']):
					messages.success(request, 'Usuario modificado')
					return HttpResponseRedirect(f'/direcsdasdastivoasdasdver/{user_log}/{nuevo_username}/')
				
				else:
					messages.success(request, 'Usuario modificado')
					return HttpResponseRedirect(f'/recaudadorver/{user_log}/{nuevo_username}/')

			else:
				messages.error(request, 'Usuario no modificado')
				if user_log.groups.filter(name__in=['Directivo']):
					return HttpResponseRedirect(f'/modificarusuario/{user_log}/{usuario}/')
				else:
					return HttpResponseRedirect(f'/modificarusuario/{user_log}/{usuario}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoInfo(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			
			context = info_direct(request, user_log)
		
			return render(request, 'ProyectoApp/directivo/directivo-info.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoEliminarUsuario(DetailView):
	def get(self, request, user_log, usuario, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			
			user_log = CustomUser.objects.get(username=user_log)
			
			usuario = CustomUser.objects.get(username=usuario)  # Usuario a eliminar
			usuario.delete()

			messages.success(request, f'El usuario {usuario.username} ha sido eliminado satisfactoriamente')
			return HttpResponseRedirect(f'/directivo{user_log}/')
		
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoVerKardex(DetailView):
	def get(self, request, user_log, user_filt, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			
			context = ver_kardex(request, user_log, user_filt)
		
			return render(request, 'ProyectoApp/directivo/directivo-ver-kardex.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoActDatos(DetailView):
	''' Vista que permite actualizar todos los datos de los usuarios a excepción de las credenciales '''
	def get(self, request, user_log, user_filt, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			
			user_filt = CustomUser.objects.get(username=user_filt)

			form = FormularioActualizarDatos(
				initial={
				'usuario_vivo': user_filt.usuario_vivo,
				'estado_usuario': user_filt.estado_usuario,
				'matricula': user_filt.matricula,
				'first_name': user_filt.first_name,
				'apell_pat': user_filt.apell_pat,
				'apell_mat': user_filt.apell_mat,
				'lugar_nac': user_filt.lugar_nac,
				'fecha_nac': user_filt.fecha_nac,
				'ci': user_filt.ci,
				'est_civil': user_filt.est_civil,
				'univ_estud': user_filt.univ_estud,
				'fecha_tg': user_filt.fecha_tg,
				'univ_lic': user_filt.univ_lic,
				'fecha_ol': user_filt.fecha_ol,
				'ent_pub': user_filt.ent_pub,
				'fecha_tit_pn': user_filt.fecha_tit_pn,
				'fecha_registro': user_filt.fecha_registro,
				'cargos_judic': user_filt.cargos_judic,
				'cargos_admin_pub': user_filt.cargos_admin_pub,
				'cargos_priv_otras': user_filt.cargos_priv_otras,
				'tiempo_ejec_prof_sd': user_filt.tiempo_ejec_prof_sd,
				'cargo_actual': user_filt.cargo_actual,
				'prod_jur': user_filt.prod_jur,
				'estud_espec': user_filt.estud_espec,
				'recon_obt': user_filt.recon_obt,
				'asist_event_inter': user_filt.asist_event_inter,
				'inst_aseg': user_filt.inst_aseg,
				'beneficiarios': user_filt.beneficiarios,
				'espec_ejer_der': user_filt.espec_ejer_der,
				'direc_ofic': user_filt.direc_ofic,
				'tel_ofic': user_filt.tel_ofic,
				'direcc': user_filt.direcc,
				'telefono': user_filt.telefono,
				'celular': user_filt.celular,
				'email': user_filt.email,
				'observ': user_filt.observ
				}
			)
			es_afiliado = CustomUser.objects.filter(groups__name='Afiliado' ,id = user_filt.id)

			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'user_filt': user_filt,
				'form': form,
				"es_afiliado":es_afiliado
				}
			return render(request, 'ProyectoApp/directivo/directivo-act-datos.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, user_filt, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			request.POST._mutable = True
			#if not validar_matricula(str(request.POST["matricula"])):
			#	messages.error(request, 'La matrícula no puede estar vacia y no puede exceder los 4 digitos')
			#	return HttpResponseRedirect(f'/rehasdamaafilant{user_log}/')

			user_mod = CustomUser.objects.get(username=user_filt)
	
			afiliado = CustomUser.objects.filter(groups__name='Afiliado' ,id = user_mod.id)
			#Es recaudador
			if len(afiliado) == 0:
				nueva_matricula = str(random.getrandbits(128))
				request.POST["matricula"] = nueva_matricula
				form = FormularioActualizarDatos(request.POST, request.FILES)

			else: 
				#Es afiliado
				form = FormularioActualizarDatos(request.POST, request.FILES)
				nueva_matricula = request.POST["matricula"]
				if len(nueva_matricula)>4:
					messages.error(request, 'La nueva matricula es mayor a 4!!!')
					return HttpResponseRedirect(f'/directactdatos/{user_log}/{user_filt}/')
			print(request.POST)
			if form.is_valid():
				
				try:
					# Datos a actualizar
					
					if form.cleaned_data['foto'] != None:
						user_mod.foto = form.cleaned_data['foto']
					
					#print("-->>>>>>>>>>>>>>>"+form.cleaned_data['fecha_nac'])
					user_mod.usuario_vivo = form.cleaned_data['usuario_vivo']
					user_mod.estado_usuario = form.cleaned_data['estado_usuario']
					user_mod.matricula = nueva_matricula
					user_mod.first_name = form.cleaned_data['first_name'].upper()
					user_mod.apell_pat = form.cleaned_data['apell_pat'].upper()
					user_mod.apell_mat = form.cleaned_data['apell_mat'].upper()
					user_mod.lugar_nac = form.cleaned_data['lugar_nac']
					user_mod.fecha_nac = form.cleaned_data['fecha_nac']
					user_mod.ci = form.cleaned_data['ci']
					user_mod.est_civil = form.cleaned_data['est_civil']
					user_mod.univ_estud = form.cleaned_data['univ_estud']
					user_mod.fecha_tg = form.cleaned_data['fecha_tg']
					user_mod.univ_lic = form.cleaned_data['univ_lic']
					user_mod.fecha_ol = form.cleaned_data['fecha_ol']
					user_mod.ent_pub = form.cleaned_data['ent_pub']
					user_mod.fecha_tit_pn = form.cleaned_data['fecha_tit_pn']
					user_mod.fecha_registro = form.cleaned_data['fecha_registro']
					user_mod.cargos_judic = form.cleaned_data['cargos_judic']
					user_mod.cargos_admin_pub = form.cleaned_data['cargos_admin_pub']
					user_mod.cargos_priv_otras = form.cleaned_data['cargos_priv_otras']
					user_mod.tiempo_ejec_prof_sd = form.cleaned_data['tiempo_ejec_prof_sd']
					user_mod.cargo_actual = form.cleaned_data['cargo_actual']
					user_mod.prod_jur = form.cleaned_data['prod_jur']
					user_mod.estud_espec = form.cleaned_data['estud_espec']
					user_mod.recon_obt = form.cleaned_data['recon_obt']
					user_mod.asist_event_inter = form.cleaned_data['asist_event_inter']
					user_mod.inst_aseg = form.cleaned_data['inst_aseg']
					user_mod.beneficiarios = form.cleaned_data['beneficiarios']
					user_mod.espec_ejer_der = form.cleaned_data['espec_ejer_der']
					user_mod.direc_ofic = form.cleaned_data['direc_ofic']
					user_mod.tel_ofic = form.cleaned_data['tel_ofic']
					user_mod.direcc = form.cleaned_data['direcc']
					user_mod.telefono = form.cleaned_data['telefono']
					user_mod.celular = form.cleaned_data['celular']
					user_mod.email = form.cleaned_data['email']
					user_mod.observ = form.cleaned_data['observ']
					
					user_mod.save()
					
					messages.success(request, '¡Datos actualizados correctamente!')
					return HttpResponseRedirect(f'/directverkardex/{user_log}/{user_filt}/')

				except Exception as e:
					if str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.matricula':
						messages.error(
							request, f'Ya existe un colegiado con esa matrícula')
						return HttpResponseRedirect(f'/directactdatos/{user_log}/{user_filt}/')
						
					elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.ci':
						messages.error(
							request, f'Ya existe un colegiado con ese C.I')
						return HttpResponseRedirect(f'/directactdatos/{user_log}/{user_filt}/')
					
					elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.username':
							
							messages.error(request, 'Ya existe un colegiado con ese username')
							return HttpResponseRedirect(f'/directactdatos/{user_log}/{user_filt}/')

					else:
						messages.error(request, 'Error al intentar actualizar')
						return HttpResponseRedirect(f'/directactdatos/{user_log}/{user_filt}/')

			else:
				messages.error(request, 'Error al intentar actualizar!!!!')
				return HttpResponseRedirect(f'/directactdatos/{user_log}/{user_filt}/')
				
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class DirectivoEnviarHistorialRecaud(DetailView):
	def get(self, request, user_log, user_filt, th, tam, mes, start_date, end_date, *args, **kwargs):
		''' ENVIA AL CORREO DEL RECAUDADOR EL HISTORIAL DE SUS APORTES MENSUALES '''

		try:

			x = enviar_historial_recaudador(
				request, user_log, user_filt, tam, mes, start_date, end_date
				)

			if x == 1:
				messages.success(request, 'Se ha enviado el historial correctamente')
				return HttpResponseRedirect(f'/directivoverrecaud/{user_log}/{user_filt}/{tam}/{th}/{start_date}/{end_date}/')

			else:
				messages.error(request, 'No se ha podido enviar el historial')
				return HttpResponseRedirect(f'/directivoverrecaud/{user_log}/{user_filt}/{tam}/{th}/{start_date}/{end_date}/')

		except Exception as e:
			messages.error(request, 'No se ha podido enviar el historial')
			return HttpResponseRedirect(f'/directivoverrecaud/{user_log}/{user_filt}/{tam}/{th}/{start_date}/{end_date}/')

class DirectivoEnviarHistorialAfil(DetailView):
	def get(self, request, user_log, user_filt, th, tam, mes, start_date, end_date, *args, **kwargs):
		''' ENVIA AL CORREO DEL AFILIADO EL HISTORIAL DE SUS APORTES MENSUALES '''

		try:

			x = enviar_historial_afiliado(
				request, user_log, user_filt, tam, mes, start_date, end_date
				)

			if x == 1:
				messages.success(request, 'Se ha enviado el historial correctamente')
				return HttpResponseRedirect(f'/directivoverafil/{user_log}/{user_filt}/{tam}/{th}/{start_date}/{end_date}/')
				
			else:
				messages.error(request, 'No se ha podido enviar el comprobante')
				return HttpResponseRedirect(f'/directivoverafil/{user_log}/{user_filt}/{tam}/{th}/{start_date}/{end_date}/')

		except Exception as e:
			messages.error(request, 'No se ha podido enviar el comprobante')
			return HttpResponseRedirect(f'/directivoverafil/{user_log}/{user_filt}/{tam}/{th}/{start_date}/{end_date}/')

class DirectivoFechas(DetailView):
	def get(self, request, user_log, user_filt, tam, th, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			try:
				
				user_log = CustomUser.objects.get(username=user_log)
				form = FormularioFechas()

				context = {
					'user_log': user_log,
					'form': form
				}

				return render(request, 'ProyectoApp/directivo/directivo-fechas.html', context)

			except:
				messages.info(request, 'Error')
				return HttpResponseRedirect(f'directivo/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, user_filt, tam, th, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo']):
			form = FormularioFechas(request.POST)

			if form.is_valid():
				
				user_log = CustomUser.objects.get(username=user_log)
				user_filt = CustomUser.objects.get(username=user_filt)

				start_date = form.cleaned_data['fecha1']
				end_date = form.cleaned_data['fecha2']

				if user_filt.groups.filter(name__in=['Recaudador']):
					context = historial_recaud_fechas(request, user_log, user_filt, tam, th, start_date, end_date)

					return render(request, 'ProyectoApp/directivo/directivo-historial-recaudador.html', context)

				else:
					context = historial_afil_fechas(request, user_log, user_filt, tam, th, start_date, end_date)

					return render(request, 'ProyectoApp/directivo/directivo-historial-afiliado.html', context)
					
			else:
				messages.error('Error')
				return HttpResponseRedirect(f'directivo/{user_log}/')


# --------------------------------------------- VISTAS PARA RECAUDADORES -----------------------------------

class RecaudadorBienvenida(ListView):
	''' Ventana de bienvenida cada vez que un Recaudador ingresa al sitio web '''
	def get(self, request, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			user_log = CustomUser.objects.get(username=request.user)
		
			context = {
				'user_log': user_log
			}

			return render(request, 'ProyectoApp/recaudador/recaudador-bienvenida.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorDashboard(DetailView):
	''' Información relacionada a su rol de Recaudador '''
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			context = generar_info_recaud(request, user_log)  # Carga toda su información
			
			recaudador = CustomUser.objects.get(username=user_log)

			return render(request, 'ProyectoApp/recaudador/recaudador-dashboard.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorVerMiKardex(DetailView):
	def get(self, request, user_log, *args, **kwargs):

		if request.user.groups.filter(name__in=['Recaudador']):

			context = {
				'user_log': CustomUser.objects.get(username=user_log)
			}
			
			return render(request, 'ProyectoApp/recaudador/recaudador-ver-mi-kardex.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorFiltrarUsuarioCI(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioFiltrarUsuarioCI()
			
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/recaudador/recaudador-filtrar-ci.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioFiltrarUsuarioCI(request.POST)

			if form.is_valid():
				ci = form.cleaned_data['ci']

				try:
					user_get = CustomUser.objects.get(ci=ci)
					user_filt = user_get.username

					if user_get.groups.filter(name__in=['Afiliado']):
						return HttpResponseRedirect(f'/recaudadorget/{user_log}/{user_filt}/')
					else:
						messages.info(request, f'No tienes permiso para acceder a ese usuario')
						return HttpResponseRedirect(f'/recaudadorfindci/{user_log}/')

				except:
					messages.info(request, f'No existe un usuario con C.I.:{ci}')
					return HttpResponseRedirect(f'/recaudadorfindci/{user_log}/')
						
			else:
				messages.error(request, f'Datos introducidos incorrectamente')
				return HttpResponseRedirect(f'/recaudadorfindci/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorFiltrarUsuarioMAT(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioFiltrarUsuarioMAT()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/recaudador/recaudador-filtrar-mat.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioFiltrarUsuarioMAT(request.POST)

			if form.is_valid():
				mat = form.cleaned_data['matricula']

				try:
					user_get = CustomUser.objects.get(matricula=mat)
					user_filt = user_get.username
					
					if user_get.groups.filter(name__in=['Afiliado']):
						return HttpResponseRedirect(f'/recaudadorget/{user_log}/{user_filt}/')
					else:
						messages.info(request, f'No tienes permiso para acceder a ese usuario')
						return HttpResponseRedirect(f'/recaudadorfindmat/{user_log}/')

				except:
					messages.info(request, f'No existe un usuario matrícula= {mat}')
					return HttpResponseRedirect(f'/recaudadorfindmat/{user_log}/')

				
											
			else:
				messages.error(request, f'Datos introducidos incorrectamente')
				return HttpResponseRedirect(f'/recaudadorfindmat/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorFiltrarUsuarioApellPat(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioFiltrarUsuarioApellPat()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/recaudador/recaudador-filtrar-apell-pat.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioFiltrarUsuarioApellPat(request.POST)

			if form.is_valid():
				apell_pat = form.cleaned_data['apell_pat']

				try:
					user_log = CustomUser.objects.get(username=user_log)
					user_filts = CustomUser.objects.filter(apell_pat__iexact=apell_pat, groups__name__in=['Afiliado'])

					if len(user_filts) == 0:
						messages.info(request, f'No existe un afiliado con apellido paterno: {apell_pat}')
						return HttpResponseRedirect(f'/reccauddd0rfiltapellpat{user_log}')

					else:
						context = {
							'user_log': user_log,
							'user_filts': user_filts
						}

						return render(
							request, 
							'ProyectoApp/recaudador/recaudador-dashboard-filtrado-apell-pat.html',
							context
						)

				except:
					messages.info(request, f'No existe algún afiliado con apellido paterno: {apell_pat}')
					return HttpResponseRedirect(f'/reccauddd0rfiltapellpat{user_log}')

				return HttpResponseRedirect(f'/recaudadorget/{user_log}/{user_filt}/')
				
			else:
				messages.error(request, 'Sólo letras')
				return HttpResponseRedirect(f'/reccauddd0rfiltapellpat{user_log}')
		else:
			return HttpResponse('No tienes permiso para acceder a este usuario')

class RecaudadorFiltrarComprobante(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioFiltrarComprobante()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/recaudador/recaudador-filtrar-comp.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioFiltrarComprobante(request.POST)

			if form.is_valid():
				comp = form.cleaned_data['comprobante']

				try:
					
					user_log = CustomUser.objects.get(username=user_log)
					aporte = AporteAfiliado.objects.get(comprobante=comp)
					recaudador = CustomUser.objects.get(username=aporte.recaudador)
					afiliado = CustomUser.objects.get(username=aporte.afiliado)
					
					context = {
						'user_log': user_log,
						'comprobante': comp,
						'aporte': aporte,
						'recaudador': recaudador,
						'afiliado': afiliado
					}
					
					return render(request, 'ProyectoApp/recaudador/recaudador-dashboard-comprobante.html', context)
				except:
					messages.info(request, f'No existe un aporte mensual con comprobante = {comp}')
					return HttpResponseRedirect(f'/recauddorfiltcomp{user_log}/')
			else:
				messages.error(request, 'Debe tener seis (06) dígitos')
				return HttpResponseRedirect(f'/recauddorfiltcomp{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorFiltrarTalonario(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioFiltrarTalonario()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/recaudador/recaudador-filtrar-talon.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioFiltrarTalonario(request.POST)

			if form.is_valid():
				talon = form.cleaned_data['talonario']

				try:
					
					user_log = CustomUser.objects.get(username=user_log)
					aportes = AporteAfiliado.objects.filter(talonario__icontains=talon)
					
					paginator = Paginator(aportes, 15)  # Mostrará hasta 15 aportes por pág.
					page = request.GET.get('page')
					aportes = paginator.get_page(page)

					context = {
						'user_log': user_log,
						'talonario': talon,
						'aportes': aportes,
					}
					
					return render(request, 'ProyectoApp/recaudador/recaudador-dashboard-talonario.html', context)
				except:
					messages.info(request, f'No existe un aporte mensual con talonario = {talon}')
					return HttpResponseRedirect(f'/recauddorfilttalon{user_log}/')
			else:
				messages.error(request, 'Debe tener seis (06) dígitos')
				return HttpResponseRedirect(f'/recauddorfilttalon{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorTipoAfiliado(DetailView):
	''' Elegir si el afiliado es totalmente nuevo o si 
	proviene del anterior sistema '''
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):

			context = {
				'user_log': CustomUser.objects.get(username=user_log)
			}

			return render(request, 'ProyectoApp/recaudador/recaudador-tipo-afiliado.html', context)

		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorRegistroAfiliado(DetailView):
	''' Registro de afiliados (Font-end) '''
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioRegistroUsuario()
			
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form,
				'afiliado': True
				}
			return render(request, 'ProyectoApp/recaudador/recaudador-registrar.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
    		
			if not validar_matricula(str(request.POST["matricula"])):
				messages.error(request, 'La matrícula no puede estar vacia y no puede exceder los 4 digitos')
				return HttpResponseRedirect(f'/rehasdamaafilant{user_log}/')

			form = FormularioRegistroUsuario(request.POST, request.FILES)

			if form.is_valid():
				if form.cleaned_data['password1'] == form.cleaned_data['password2']:
					
					try:
						user_new = CustomUser.objects.create_user(
							first_name=form.cleaned_data['first_name'].upper(),
							apell_pat=form.cleaned_data['apell_pat'].upper(),
							apell_mat=form.cleaned_data['apell_mat'].upper(),
							username=form.cleaned_data['username'],
							password=form.cleaned_data['password1'],
							email=form.cleaned_data['email'],
							matricula=form.cleaned_data['matricula'],
							ci=form.cleaned_data['ci'],
							fecha_registro=form.cleaned_data['fecha_registro'],
							
							foto = form.cleaned_data['foto'],
							usuario_vivo = True,
							estado_usuario = form.cleaned_data['estado_usuario'],
							lugar_nac = form.cleaned_data['lugar_nac'],
							fecha_nac = form.cleaned_data['fecha_nac'],
							est_civil = form.cleaned_data['est_civil'],
							univ_estud = form.cleaned_data['univ_estud'],
							fecha_tg = form.cleaned_data['fecha_tg'],
							univ_lic = form.cleaned_data['univ_lic'],
							fecha_ol = form.cleaned_data['fecha_ol'],
							ent_pub = form.cleaned_data['ent_pub'],
							fecha_tit_pn = form.cleaned_data['fecha_tit_pn'],
							cargos_judic = form.cleaned_data['cargos_judic'],
							cargos_admin_pub = form.cleaned_data['cargos_admin_pub'],
							cargos_priv_otras = form.cleaned_data['cargos_priv_otras'],
							tiempo_ejec_prof_sd = form.cleaned_data['tiempo_ejec_prof_sd'],
							cargo_actual = form.cleaned_data['cargo_actual'],
							prod_jur = form.cleaned_data['prod_jur'],
							estud_espec = form.cleaned_data['estud_espec'],
							recon_obt = form.cleaned_data['recon_obt'],
							asist_event_inter = form.cleaned_data['asist_event_inter'],
							inst_aseg = form.cleaned_data['inst_aseg'],
							beneficiarios = form.cleaned_data['beneficiarios'],
							espec_ejer_der = form.cleaned_data['espec_ejer_der'],
							direc_ofic = form.cleaned_data['direc_ofic'],
							tel_ofic = form.cleaned_data['tel_ofic'],
							direcc = form.cleaned_data['direcc'],
							telefono = form.cleaned_data['telefono'],
							celular = form.cleaned_data['celular'],
							observ = form.cleaned_data['observ'],
							expedido = form.cleaned_data['expedido'],
							)

						user_new.groups.add(Group.objects.get(name='Afiliado'))
						user_new.save()
						
						messages.success(request, '¡Afiliado creado correctamente!')
						return HttpResponseRedirect(f'/recaudador/{user_log}/')

					except Exception as e:
						if str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.matricula':
							messages.error(
								request, f'Ya existe un colegiado con esa matrícula')
							return HttpResponseRedirect(f'/recaudregistafil{user_log}/')
						
						elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.ci':
							messages.error(
								request, f'Ya existe un colegiado con ese C.I')
							return HttpResponseRedirect(f'/recaudregistafil{user_log}/')
						
						elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.username':
							
							messages.error(request, 'Ya existe un colegiado con ese username')
							return HttpResponseRedirect(f'/recaudregistafil{user_log}/')

						else:
							print("Estoy dentro del except")
							print(e)
							messages.error(request, '¡Valor incorrecto en datos!')
							return HttpResponseRedirect(f'/recaudregistafil{user_log}/')
				
				else:
					messages.error(request, 'Las contraseñas no coinciden')
					return HttpResponseRedirect(f'/recaudregistafil{user_log}/')
				
			else:
				print("entre al form errors")
				print(form.errors)
				messages.error(request, '¡Valor incorrecto en datos!')
				
				return HttpResponseRedirect(f'/recaudregistafil{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorRegistroAfiliadoAntiguo(DetailView):
	''' Registro de afiliados (Font-end) '''
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioRegistroAfiliadoAntiguo()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form,
				'afiliado': True
				}
			return render(request, 'ProyectoApp/recaudador/recaudador-registrar-afil-ant.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
	
			if not validar_matricula(str(request.POST["matricula"])):
				messages.error(request, 'La matrícula no puede estar vacia y no puede exceder los 4 digitos')
				return HttpResponseRedirect(f'/rehasdamaafilant{user_log}/')

			form = FormularioRegistroAfiliadoAntiguo(request.POST, request.FILES)

			if form.is_valid():
				
				if form.cleaned_data['password1'] == form.cleaned_data['password2']:
					
					try:
						user_new = CustomUser.objects.create_user(
							first_name=form.cleaned_data['first_name'].upper(),
							apell_pat=form.cleaned_data['apell_pat'].upper(),
							apell_mat=form.cleaned_data['apell_mat'].upper(),
							username=form.cleaned_data['username'],
							password=form.cleaned_data['password1'],
							email=form.cleaned_data['email'],
							matricula=form.cleaned_data['matricula'],
							ci=form.cleaned_data['ci'],
							fecha_registro=form.cleaned_data['fecha_registro'],
							
							foto = form.cleaned_data['foto'],
							usuario_vivo = form.cleaned_data['usuario_vivo'],
							estado_usuario = form.cleaned_data['estado_usuario'],
							lugar_nac = form.cleaned_data['lugar_nac'],
							fecha_nac = form.cleaned_data['fecha_nac'],
							est_civil = form.cleaned_data['est_civil'],
							univ_estud = form.cleaned_data['univ_estud'],
							fecha_tg = form.cleaned_data['fecha_tg'],
							univ_lic = form.cleaned_data['univ_lic'],
							fecha_ol = form.cleaned_data['fecha_ol'],
							ent_pub = form.cleaned_data['ent_pub'],
							fecha_tit_pn = form.cleaned_data['fecha_tit_pn'],
							cargos_judic = form.cleaned_data['cargos_judic'],
							cargos_admin_pub = form.cleaned_data['cargos_admin_pub'],
							cargos_priv_otras = form.cleaned_data['cargos_priv_otras'],
							tiempo_ejec_prof_sd = form.cleaned_data['tiempo_ejec_prof_sd'],
							cargo_actual = form.cleaned_data['cargo_actual'],
							prod_jur = form.cleaned_data['prod_jur'],
							estud_espec = form.cleaned_data['estud_espec'],
							recon_obt = form.cleaned_data['recon_obt'],
							asist_event_inter = form.cleaned_data['asist_event_inter'],
							inst_aseg = form.cleaned_data['inst_aseg'],
							beneficiarios = form.cleaned_data['beneficiarios'],
							espec_ejer_der = form.cleaned_data['espec_ejer_der'],
							direc_ofic = form.cleaned_data['direc_ofic'],
							tel_ofic = form.cleaned_data['tel_ofic'],
							direcc = form.cleaned_data['direcc'],
							telefono = form.cleaned_data['telefono'],
							celular = form.cleaned_data['celular'],
							observ = form.cleaned_data['observ'],
							expedido = form.cleaned_data['expedido'],
							)

						user_new.groups.add(Group.objects.get(name='Afiliado'))
						user_new.save()
						
						try:
							# CARGAR LOS APORTES MENSUALES DEL ANTERIOR SISTEMA
							cargar_aportes = cobrar_aporte_mult(
								request, user_log, form.cleaned_data['username'],
								form.cleaned_data['fecha_registro'], int(form.cleaned_data['cant_aportes_iniciales']),
								'AMI', form.cleaned_data['talonario'])

						except Exception as e:
							print(e)

						messages.success(request, '¡Afiliado creado correctamente!')
						return HttpResponseRedirect(f'/recaudador/{user_log}/')
						
					except Exception as e:
						
						print(e)

						if str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.matricula':
							messages.error(
								request, f'Ya existe un colegiado con esa matrícula')
							return HttpResponseRedirect(f'/rehasdamaafilant{user_log}/')
						
						elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.ci':
							messages.error(
								request, f'Ya existe un colegiado con ese C.I')
							return HttpResponseRedirect(f'/rehasdamaafilant{user_log}/')
						
						elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.username':
							
							messages.error(request, 'Ya existe un colegiado con ese username')
							return HttpResponseRedirect(f'/rehasdamaafilant{user_log}/')
						else:
							messages.error(request, f'¡Error en datos datos!')
							return HttpResponseRedirect(f'/rehasdamaafilant{user_log}/')
				
				else:
					messages.error(request, 'Las contraseñas no coinciden')
					return HttpResponseRedirect(f'/rehasdamaafilant{user_log}/')
				
			else:
				messages.error(request, 'La matrícula no puede tener más de 4 dígitos')
				return HttpResponseRedirect(f'/rehasdamaafilant{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorDashboardFiltrado(DetailView):
	def get(self, request, user_log, user_filt, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			
			check_afil = CustomUser.objects.get(username=user_filt)
			if check_afil.groups.filter(name__in=['Afiliado']):
				
				context = filtrar_info(request, user_log, user_filt)
				
				return render(request, 'ProyectoApp/recaudador/recaudador-dashboard-filtrado.html', context)
			else:
				return HttpResponse('No tienes permiso para acceder a este usuario')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorDashboardAfiliadosDesh(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			context = generar_info_recaud_afiliados_desh(request, user_log)
			
			return render(request, 'ProyectoApp/recaudador/recaudador-dashboard-afiliados-desh.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorVerUsuario(DetailView):
	def get(self, request, user_log, usuario, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			
			context = recaudador_ver_usuario(request, user_log, usuario)

			return render(request, 'ProyectoApp/recaudador/recaudador-ver-usuario.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorModDatos(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			user_log = CustomUser.objects.get(username=user_log)
			
			form = FormularioModificarDatos(
				initial = {
				'ci': user_log.ci,
				'email': user_log.email,
				'first_name': user_log.first_name, 
				'apell_pat': user_log.apell_pat,
				'apell_mat': user_log.apell_mat,
				'telefono': user_log.telefono,
				'celular': user_log.celular,
				'direcc': user_log.direcc,			
				'lugar_nac': user_log.lugar_nac,
				'fecha_nac': user_log.fecha_nac,
				'est_civil': user_log.est_civil,
				'univ_estud': user_log.univ_estud,
				'fecha_tg': user_log.fecha_tg,
				'univ_lic': user_log.univ_lic,
				'fecha_ol': user_log.fecha_ol,
				'ent_pub': user_log.ent_pub,
				'fecha_tit_pn': user_log.fecha_tit_pn,
				'cargos_judic': user_log.cargos_judic,
				'cargos_admin_pub': user_log.cargos_admin_pub,
				'cargos_priv_otras': user_log.cargos_priv_otras,
				'tiempo_ejec_prof_sd': user_log.tiempo_ejec_prof_sd,
				'cargo_actual': user_log.cargo_actual,
				'prod_jur': user_log.prod_jur,
				'estud_espec': user_log.estud_espec,
				'recon_obt': user_log.recon_obt,
				'asist_event_inter': user_log.asist_event_inter,
				'inst_aseg': user_log.inst_aseg,
				'beneficiarios': user_log.beneficiarios,
				'espec_ejer_der': user_log.espec_ejer_der,
				'direc_ofic': user_log.direc_ofic,
				'tel_ofic': user_log.tel_ofic,			
				}
			)
			context = {
				'user_log': user_log,
				'form': form
				}
			return render(request, 'ProyectoApp/recaudador/recaudador-mod-datos.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioModificarDatos(request.POST)

			if form.is_valid():
				try:
					# Datos a cambiar
					user_mod = CustomUser.objects.get(username=user_log)
					
					user_mod.first_name = form.cleaned_data['first_name'].upper()
					user_mod.apell_pat = form.cleaned_data['apell_pat'].upper()
					user_mod.apell_mat = form.cleaned_data['apell_mat'].upper()
					user_mod.lugar_nac = form.cleaned_data['lugar_nac']
					user_mod.fecha_nac = form.cleaned_data['fecha_nac']
					user_mod.ci = form.cleaned_data['ci']
					user_mod.est_civil = form.cleaned_data['est_civil']
					user_mod.univ_estud = form.cleaned_data['univ_estud']
					user_mod.fecha_tg = form.cleaned_data['fecha_tg']
					user_mod.univ_lic = form.cleaned_data['univ_lic']
					user_mod.fecha_ol = form.cleaned_data['fecha_ol']
					user_mod.ent_pub = form.cleaned_data['ent_pub']
					user_mod.fecha_tit_pn = form.cleaned_data['fecha_tit_pn']
					user_mod.cargos_judic = form.cleaned_data['cargos_judic']
					user_mod.cargos_admin_pub = form.cleaned_data['cargos_admin_pub']
					user_mod.cargos_priv_otras = form.cleaned_data['cargos_priv_otras']
					user_mod.tiempo_ejec_prof_sd = form.cleaned_data['tiempo_ejec_prof_sd']
					user_mod.cargo_actual = form.cleaned_data['cargo_actual']
					user_mod.prod_jur = form.cleaned_data['prod_jur']
					user_mod.estud_espec = form.cleaned_data['estud_espec']
					user_mod.recon_obt = form.cleaned_data['recon_obt']
					user_mod.asist_event_inter = form.cleaned_data['asist_event_inter']
					user_mod.inst_aseg = form.cleaned_data['inst_aseg']
					user_mod.beneficiarios = form.cleaned_data['beneficiarios']
					user_mod.espec_ejer_der = form.cleaned_data['espec_ejer_der']
					user_mod.direc_ofic = form.cleaned_data['direc_ofic']
					user_mod.tel_ofic = form.cleaned_data['tel_ofic']
					user_mod.direcc = form.cleaned_data['direcc']
					user_mod.telefono = form.cleaned_data['telefono']
					user_mod.celular = form.cleaned_data['celular']
					user_mod.email = form.cleaned_data['email']
					
					user_mod.save()

					messages.success(request, 'Datos actualizados correctamente')
					return HttpResponseRedirect(f'/recaudador/{user_log}/')

				except Exception as e:
					if str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.matricula':
						messages.error(
							request, f'Ya existe un colegiado con esa matrícula')
						return HttpResponseRedirect(f'/recaudadormoddatos/{user_log}/')
						
					elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.ci':
						messages.error(
							request, f'Ya existe un colegiado con ese C.I')
						return HttpResponseRedirect(f'/recaudadormoddatos/{user_log}/')
					
					elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.username':
							
							messages.error(request, 'Ya existe un colegiado con ese username')
							return HttpResponseRedirect(f'/recaudadormoddatos/{user_log}/')

					else:
						print(e)
						messages.error(request, 'Datos incorrectos')
						return HttpResponseRedirect(f'/recaudadormoddatos/{user_log}/')
											
			else:
				messages.error(request, 'Datos ingresados erróneamente')
				return HttpResponseRedirect(f'/recaudadormoddatos/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorModClave(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioModificarClave()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/recaudador/recaudador-mod-clave.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioModificarClave(request.POST)

			if form.is_valid():
				
				if form.cleaned_data['password1'] == form.cleaned_data['password2']:
					
					recaudador = CustomUser.objects.get(username=user_log)
					
					if recaudador.check_password(form.cleaned_data['password1']):
						
						if form.cleaned_data['password_new1'] == form.cleaned_data['password_new2']:
					
							recaudador.password = make_password(
										form.cleaned_data['password_new1'],
										salt=None,
										hasher='default'
									)
								
							recaudador.save()

							messages.success(request, 'Clave actualizada')
							return HttpResponseRedirect(f'/recaudador/{user_log}/')

						else:
							messages.error(request, 'Las claves no coinciden')
							return HttpResponseRedirect(f'/recaudadormodclave/{user_log}/')

					else:
						messages.error(request, 'Error en la verificación de tu clave actual')
						return HttpResponseRedirect(f'/recaudadormodclave/{user_log}/')

				else:
					messages.error(request, 'Las claves actuales no coinciden')
					return HttpResponseRedirect(f'/recaudadormodclave/{user_log}/')

			else:
				messages.error(request, 'Datos introducidos erróneamente')
				return HttpResponseRedirect(f'/recaudadormodclave/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorModFoto(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioSubirFoto()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form
				}
			return render(request, 'ProyectoApp/recaudador/recaudador-mod-foto.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioSubirFoto(request.POST, request.FILES)

			if form.is_valid():
				try:
					
					user_mod = CustomUser.objects.get(username=user_log)
					user_mod.foto = form.cleaned_data['foto']

					user_mod.save()

				except:
					messages.error(request, 'Error al intentar subir su foto')
					return HttpResponseRedirect(f'/recaudmodfoto/{user_log}/')

				messages.success(request, 'Foto actualizada')
				return HttpResponseRedirect(f'/recaudador/{user_log}/')
											
			else:
				messages.error(request, 'Error al intentar subir su foto')
				return HttpResponseRedirect(f'/recaudmodfoto/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorRegistrarCobro(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			
			form = FormularioRegistrarCobro()
			user_log = CustomUser.objects.get(username=user_log)
			aporte_amu = AporteMensual.objects.get(aporte_mensual_deno='AMU')
			#aporte_ami = AporteMensual.objects.get(aporte_mensual_deno='AMI')

			context = {
				'user_log': user_log,
				'aporte_amu': aporte_amu,
			#	'aporte_ami': aporte_ami,
				'form': form
			}

			return render(request, 'ProyectoApp/recaudador/recaudador-registrar-cobro.html', context)

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioRegistrarCobro(request.POST)

			if form.is_valid():

				if form.cleaned_data['opcion'] == 'C.I.':
					return HttpResponseRedirect(f'/recaudadorfindci/{user_log}/')
					
				
				elif form.cleaned_data['opcion'] == 'N° Matrícula ICAP':
					return HttpResponseRedirect(f'/recaudadorfindmat/{user_log}/')

				else:
					return HttpResponseRedirect(f'/reccauddd0rfiltapellpat{user_log}/')

			else:
				messages.error(request, 'Vuelva a intentarlo')
				return HttpResponseRedirect(f'/recaudadregiscobro{user_log}/')

class RecaudadorCobrar(DetailView):
	def get(self, request, user_log, usuario, ta, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			print("ebtre alk errir")
			user_log = CustomUser.objects.get(username=user_log)
			usuario = CustomUser.objects.get(username=usuario)

			if ta == 1:
				# APORTE MENSUAL
				form = FormularioCobrarAM()
				aporte_amu = AporteMensual.objects.get(aporte_mensual_deno='AMU')
				#aporte_ami = AporteMensual.objects.get(aporte_mensual_deno='AMI')

				context = {
				'form':form,
				'user_log': user_log, 
				'usuario': usuario,
				'ta': ta,
				'aporte_amu': aporte_amu,
				#'aporte_ami': aporte_ami
				}

			elif ta == 2:
				# APORTE CERTIFICADO
				form = FormularioCobrarAC()
				aporte_cert = AporteCertificacion.objects.get(aporte_certificacion_deno='CERTIFICADO')
				
				context = {
				'form':form,
				'user_log': user_log, 
				'usuario': usuario,
				'ta': ta,
				'aporte_cert': aporte_cert
				}

			else:
				# APORTE DONACIÓN
				form = FormularioCobrarAD()

				context = {
				'form':form,
				'user_log': user_log, 
				'usuario': usuario,
				'ta': ta,
				'etiqueta': None
				}

			return render(request, 'ProyectoApp/recaudador/recaudador-cobro-confirmar.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, usuario, ta, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			if len(request.POST["numero_recibo"]) >5:
				messages.error(request, 'El numero de recibo tiene mas de 5 digitos , maximo debe tener 5 ')
				return HttpResponseRedirect(f'/recaudadorcobrar/{user_log}/{usuario}{ta}/')
			if ta == 1:
				# APORTE MENSUAL
				form = FormularioCobrarAM(request.POST)
			elif ta == 2:
				# APORTE CERTIFICADO
				form = FormularioCobrarAC(request.POST)
			else:
				# APORTE DONACIÓN
				form = FormularioCobrarAD(request.POST)
				

			if form.is_valid():
				
				fecha_pago = form.cleaned_data['fecha_pago']
				talon = form.cleaned_data['talonario']
				numero_recibo = form.cleaned_data["numero_recibo"]
				if ta == 1:  # Es un aporte mensual
					etiq = form.cleaned_data['aporte_mensual_deno']
					
				elif ta == 3:  # Es un aporte por donación
					etiq = form.cleaned_data['aporte_dona_afil']
				
				else:  # Es un aporte por certificación
					etiq = None

				return HttpResponseRedirect(
						f'/recaudadorcobrarconfdatos/{user_log}/{usuario}{ta}/{talon}/{fecha_pago}/{etiq}/{numero_recibo}'
					)
				
			else:
				messages.error(request, 'Cobro no procesado')
				return HttpResponseRedirect(f'/recaudadorcobrar/{user_log}/{usuario}{ta}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorCobroConfirmarDatos(DetailView):
	
	def get(self, request, user_log, usuario, ta, talon, fecha_pago, etiq,numero_recibo ,*args, **kwargs):
		
		if request.user.groups.filter(name__in=['Recaudador']):
			cant =1
			querie  =CustomUser.objects.filter(username=usuario).first()
			facturas_emitidas_afiliado = AporteAfiliado.objects.filter(
				afiliado_id=querie.id
			)
			if len(facturas_emitidas_afiliado) == 0:
				#El afiliado no tiene ninguna factura pagada
				# Obtenemos la fecha de registro
				d1 = datetime.date(querie.fecha_registro.year, querie.fecha_registro.month, 10)
				#Obtenemos el dia de hoy
				today = date.today()
				d2 = datetime.date(today.year, today.month, 10)
				#Sacamos los meses de diferencia
				months = rrule.rrule(rrule.MONTHLY, dtstart=d1, until=d2).count()
				#Obtenemos la fecha de registro de la tabla fechas que hemos creado
				fecha = Fechas.objects.filter(agno=querie.fecha_registro.year,mes = querie.fecha_registro.month).first()
				#Sacamos todas las fechas a pagar
				fechas = [fecha.id+i for i in range(cant)]
				#Las filtramos en fechas para saber que meses va a pagar
				fechas_pagar = Fechas.objects.filter(
					id__in = fechas
				)
			else:
				#Aca debe de ir cuando el afiliado ya tenga facturas pagadas que debe de hacerse
				fecha = Fechas.objects.filter(agno=querie.fecha_registro.year,mes = querie.fecha_registro.month).first()
				#Ultima fecha pagada 
				val = fecha.id + len(facturas_emitidas_afiliado)
				# Fechas a pagar
				fechas = [val+i for i in range(cant)]
				fechas_pagar = Fechas.objects.filter(
					id__in = fechas
				)
				# Fechas que ya pago 
				# fechas = [fecha.id+i for i in range(len(facturas_emitidas_afiliado))]
				# Fechas que va a pagar 

				pass
			meses_pago = fechas_pagar[0]
			print(fecha_pago)
			user_log = CustomUser.objects.get(username=user_log)
			usuario = CustomUser.objects.get(username=usuario)

			if ta == 1:  # Es un aporte mensual
				am = AporteMensual.objects.get(aporte_mensual_deno=f'{etiq}')

				context = {
					'user_log': user_log,
					'usuario': usuario,
					'ta': ta,
					'talonario': talon,
					'numero_recibo':numero_recibo,
					'fecha_pago': fecha_pago,
					'am': am,
					'etiqueta': etiq,
					'meses_pago':meses_pago
					
					
				}

			elif ta == 2:  # Es un aporte por certificación
				aporte_cert = AporteCertificacion.objects.get(aporte_certificacion_deno='CERTIFICADO')

				context = {
					'user_log': user_log,
					'usuario': usuario,
					'ta': ta,
					'talonario': talon,
					'fecha_pago': fecha_pago,
					'aporte_cert': aporte_cert,
				}

			else:  # Es un aporte por donación
				context = {
					'user_log': user_log,
					'usuario': usuario,
					'ta': ta,
					'talonario': talon,
					'fecha_pago': fecha_pago,
					'aporte_dona_afil': etiq
				}
			
			messages.info(request, 'Revise los datos y proceda a ejecutar...')
			return render(request, 'ProyectoApp/recaudador/recaudador-cobro-confirmar-datos.html', context)
		
	def post(self, request, user_log, usuario, ta, talon, fecha_pago, etiq,numero_recibo ,*args, **kwargs):
	
		if request.user.groups.filter(name__in=['Recaudador']):
	
			context = cobrar_aporte_confirmado(request, user_log, usuario, ta, talon, fecha_pago, etiq,numero_recibo)
			comprobante = context['comprobante']

			messages.success(request, 'Cobro efectuado correctamente')
			return HttpResponseRedirect(f'/recaudadorcobroefectuado/{user_log}/{comprobante}/')

class RecaudadorCobroMultiple(DetailView):
	def get(self, request, user_log, usuario, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			
			form = FormularioCobroMult()
			user_log = CustomUser.objects.get(username=user_log)
			usuario = CustomUser.objects.get(username=usuario)
			aporte_amu = AporteMensual.objects.get(aporte_mensual_deno='AMU')
			#aporte_ami = AporteMensual.objects.get(aporte_mensual_deno='AMI')

			context = {
				'user_log': user_log,
				'usuario': usuario,
				'aporte_amu': aporte_amu,
				#'aporte_ami': aporte_ami,
				'form': form
			}

			return render(request, 'ProyectoApp/recaudador/recaudador-cobro-mult-fechas.html', context)

	def post(self, request, user_log, usuario, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioCobroMult(request.POST)
			if form.is_valid():

				fecha_pago = form.cleaned_data['fecha_pago']
				cant = form.cleaned_data['cantidad']
				tam = form.cleaned_data['aporte_mensual_deno']
				talon = form.cleaned_data['talonario']
				numero_recibo = form.cleaned_data['numero_recibo']

				messages.info(request, 'Revise los datos y proceda a ejecutar...')
				return HttpResponseRedirect(f'/recaudadorcobromultefect/{user_log}/{usuario}/{fecha_pago}/{cant}/{tam}/{talon}/{numero_recibo}')
				
			else:
				messages.error(request, 'Error en fecha. DEBE SER YYYY-MM-DD')
				return HttpResponseRedirect(f'/recaudadorcobromult/{user_log}/{usuario}/')
						
class RecaudadorCobroMultipleEfect(DetailView):

	def get(self, request, user_log, usuario, fecha_pago, cant, tam, talon,numero_recibo):
		
		if request.user.groups.filter(name__in=['Recaudador']):
			querie  =CustomUser.objects.filter(username=usuario).first()
			facturas_emitidas_afiliado = AporteAfiliado.objects.filter(
				afiliado_id=querie.id
			)
			if len(facturas_emitidas_afiliado) == 0:
				#El afiliado no tiene ninguna factura pagada
				# Obtenemos la fecha de registro
				d1 = datetime.date(querie.fecha_registro.year, querie.fecha_registro.month, 10)
				#Obtenemos el dia de hoy
				today = date.today()
				d2 = datetime.date(today.year, today.month, 10)
				#Sacamos los meses de diferencia
				months = rrule.rrule(rrule.MONTHLY, dtstart=d1, until=d2).count()
				#Obtenemos la fecha de registro de la tabla fechas que hemos creado
				fecha = Fechas.objects.filter(agno=querie.fecha_registro.year,mes = querie.fecha_registro.month).first()
				#Sacamos todas las fechas a pagar
				fechas = [fecha.id+i for i in range(cant)]
				#Las filtramos en fechas para saber que meses va a pagar
				fechas_pagar = Fechas.objects.filter(
					id__in = fechas
				)
			else:
				#Aca debe de ir cuando el afiliado ya tenga facturas pagadas que debe de hacerse
				fecha = Fechas.objects.filter(agno=querie.fecha_registro.year,mes = querie.fecha_registro.month).first()
				#Ultima fecha pagada 
				val = fecha.id + len(facturas_emitidas_afiliado)
				# Fechas a pagar
				fechas = [val+i for i in range(cant)]
				fechas_pagar = Fechas.objects.filter(
					id__in = fechas
				)
				# Fechas que ya pago 
				# fechas = [fecha.id+i for i in range(len(facturas_emitidas_afiliado))]
				# Fechas que va a pagar 

				pass
			user_log = CustomUser.objects.get(username=user_log)
			usuario = CustomUser.objects.get(username=usuario)
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno=tam)

			context = {
				'user_log': user_log,
				'usuario': usuario,
				'fecha_pago': fecha_pago,
				'cant': cant,
				'monto': cant * int(tipo_factura.aporte_mensual),
				'talonario': talon,
				'numero_recibo': numero_recibo,
				'fechas_pagar':fechas_pagar
			}
			
			return render(request, 'ProyectoApp/recaudador/recaudador-cobro-mult-confirmar.html', context)

	def post(self, request, user_log, usuario, fecha_pago, cant, tam, talon,numero_recibo):
		querie  =CustomUser.objects.filter(username=usuario).first()
		facturas_emitidas_afiliado = AporteAfiliado.objects.filter(
			afiliado_id=querie.id
		)
		if len(facturas_emitidas_afiliado) == 0:
			#El afiliado no tiene ninguna factura pagada
			# Obtenemos la fecha de registro
			d1 = datetime.date(querie.fecha_registro.year, querie.fecha_registro.month, 10)
			#Obtenemos el dia de hoy
			today = date.today()
			d2 = datetime.date(today.year, today.month, 10)
			#Sacamos los meses de diferencia
			months = rrule.rrule(rrule.MONTHLY, dtstart=d1, until=d2).count()
			#Obtenemos la fecha de registro de la tabla fechas que hemos creado
			fecha = Fechas.objects.filter(agno=querie.fecha_registro.year,mes = querie.fecha_registro.month).first()
			#Sacamos todas las fechas a pagar
			fechas = [fecha.id+i for i in range(cant)]
			#Las filtramos en fechas para saber que meses va a pagar
			fechas_pagar = Fechas.objects.filter(
				id__in = fechas
			)
		else:
			#Aca debe de ir cuando el afiliado ya tenga facturas pagadas que debe de hacerse
			fecha = Fechas.objects.filter(agno=querie.fecha_registro.year,mes = querie.fecha_registro.month).first()
			#Ultima fecha pagada 
			val = fecha.id + len(facturas_emitidas_afiliado)
			# Fechas a pagar
			fechas = [val+i for i in range(cant)]
			fechas_pagar = Fechas.objects.filter(
				id__in = fechas
			)
			# Fechas que ya pago 
			# fechas = [fecha.id+i for i in range(len(facturas_emitidas_afiliado))]
			# Fechas que va a pagar 

			pass
		print(fechas_pagar)
		context = cobrar_aporte_mult(request, user_log, usuario, fecha_pago, cant, tam, talon,numero_recibo,fechas_pagar )
		print("\n\n\n\n\n\n")
		messages.success(request, 'Cobro múltiple efectuado correctamente')
		return HttpResponseRedirect(f'/recaudador/{user_log}/')

class RecaudadorCobroEfectuado(DetailView):
	def get(self, request, user_log, comprobante, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			user_log = CustomUser.objects.get(username=user_log)
			aporte = AporteAfiliado.objects.get(comprobante=comprobante)
			afiliado = CustomUser.objects.get(username=aporte.afiliado)
			print(aporte)
			context = {
				'user_log': user_log,
				'afiliado': afiliado,
				'aporte': aporte
				}

			return render(request, 'ProyectoApp/recaudador/recaudador-cobro-efectuado.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorInfo(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
		
			context = info_recaud(request, user_log)

			return render(request, 'ProyectoApp/recaudador/recaudador-info.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorDetalles(DetailView):
	def get(self, request, user_log, comprobante, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			
			user_log = CustomUser.objects.get(username=user_log)
			info = AporteAfiliado.objects.get(comprobante=comprobante)

			context = {
				'user_log': user_log,
				'info': info
			}

			return render(request, 'ProyectoApp/recaudador/recaudador-detalles.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorVerHistorial(DetailView):
	''' MUESTRA EL HISTORIAL DE APORTES DEL AFILIADO (MENSUALES) '''

	def get(self, request, user_log, afiliado, tam, th, start_date, end_date, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			try:
				
				if th == 'TOTAL':
					context = historial_afil(request, user_log, afiliado, tam, th)

				elif th == 'MES':
					context = historial_afil_mes(request, user_log, afiliado, tam, th)

				else:
					context = historial_afil_fechas(request, user_log, afiliado, tam, th, start_date, end_date)

				return render(request, 'ProyectoApp/recaudador/recaudador-ver-historial.html', context)

			except:
				messages.error(request, 'No hay registro de aportes mensuales para este afiliado')
				return HttpResponseRedirect(f'recaudador/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorDashboardMisCobros(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			try:
				context = cal_mis_cobros(request, user_log)

				return render(request, 'ProyectoApp/recaudador/recaudador-dashboard-mis-cobros.html', context)

			except:
				messages.info(request, 'No hay registro de mis cobros')
				return HttpResponseRedirect(f'recaudador/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorDashboardMisCobrosMes(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			try:
				context = cal_mis_cobros_mes(request, user_log)

				return render(request, 'ProyectoApp/recaudador/recaudador-dashboard-mis-cobros.html', context)

			except:
				messages.info(request, 'No hay registro de mis cobros')
				return HttpResponseRedirect(f'recaudador/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorDashboardMisCobrosFechas(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			try:
				
				user_log = CustomUser.objects.get(username=user_log)
				form = FormularioFechas()

				context = {
					'user_log': user_log,
					'form': form
				}

				return render(request, 'ProyectoApp/recaudador/recaudador-dashboard-mis-cobros-fechas.html', context)

			except:
				messages.info(request, 'No hay registro de mis cobros')
				return HttpResponseRedirect(f'recaudador/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioFechas(request.POST)

			if form.is_valid():
				
				context = cal_mis_cobros_fechas(request, user_log, form.cleaned_data['fecha1'], form.cleaned_data['fecha2'])

				return render(request, 'ProyectoApp/recaudador/recaudador-dashboard-mis-cobros.html', context)
			else:
				messages.error('No se han encontrado registros')
				return HttpResponseRedirect(f'/reca2ud2a1dorget/{user_log}/')

class DirectivoExportarHistorialRecaud(DetailView):
	def get(self, request, user_log, user_filt, tam, mes, start_date, end_date, *args, **kwargs):
		''' EXPORTA TODOS LOS APORTES MENSUALES REALIZADOS POR EL RECAUDADOR '''
		if request.user.groups.filter(name__in=['Directivo']):
			
			template = get_template('ProyectoApp/historial.html')

			context = exportar_historial_recaud(
				request, user_log, user_filt, tam, mes, start_date, end_date
				)

			html = template.render(context)
			pdf = generar_pdf('ProyectoApp/directivo/historial-recaudaciones.html', context)
			
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = f'historial_{user_filt}.pdf'
				content = f'attachment; filename={filename}'
				response['Content-Disposition'] = content
				return response
			else:
				return HttpResponse('Error')

class DirectivoExportarHistorialAfil(DetailView):
	def get(self, request, user_log, user_filt, tam, mes, start_date, end_date, *args, **kwargs):
		''' EXPORTA TODOS LOS APORTES MENSUALES REALIZADOS POR EL AFILIADO '''
		if request.user.groups.filter(name__in=['Directivo']):
			
			template = get_template('ProyectoApp/historial.html')

			context = recaud_exportar_historial_afil(
				request, user_log, user_filt, tam, mes, start_date, end_date
				)

			html = template.render(context)
			pdf = generar_pdf('ProyectoApp/historial.html', context)
			
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = f'historial_{user_filt}.pdf'
				content = f'attachment; filename={filename}'
				response['Content-Disposition'] = content
				return response
			else:
				return HttpResponse('Error')

class RecaudadorExportarHistorialAfil(DetailView):
	def get(self, request, user_log, user_filt, tam, mes, start_date, end_date, *args, **kwargs):
		''' EXPORTA TODOS LOS APORTES MENSUALES REALIZADOS POR EL AFILIADO '''
		if request.user.groups.filter(name__in=['Recaudador']):
			
			template = get_template('ProyectoApp/historial.html')

			context = recaud_exportar_historial_afil(
				request, user_log, user_filt, tam, mes, start_date, end_date
				)

			html = template.render(context)
			pdf = generar_pdf('ProyectoApp/historial.html', context)
			
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = f'historial_{user_filt}.pdf'
				content = f'attachment; filename={filename}'
				response['Content-Disposition'] = content
				return response
			else:
				return HttpResponse('Error')

class RecaudadorEnviarHistorialAfil(DetailView):
	def get(self, request, user_log, user_filt, th, tam, start_date, end_date, *args, **kwargs):
		''' ENVIA AL CORREO DEL AFILIADO EL HISTORIAL DE SUS APORTES MENSUALES '''
		
		try:

			x = enviar_historial_afiliado(
				request, user_log, user_filt, tam, th, start_date, end_date
				)

			if x == 1:
				messages.success(request, 'Se ha enviado el historial correctamente')
				return HttpResponseRedirect(f'/recaudaviewhistory/{user_log}/{user_filt}/{tam}/{th}/{start_date}/{end_date}/')
			
			else:
				messages.error(request, 'No se ha podido enviar el comprobante')
				return HttpResponseRedirect(f'/recaudaviewhistory/{user_log}/{user_filt}/{tam}/{th}/{start_date}/{end_date}/')

		except Exception as e:
			messages.error(request, 'No se ha podido enviar el comprobante')
			return HttpResponseRedirect(f'/recaudaviewhistory/{user_log}/{user_filt}/{tam}/{th}/{start_date}/{end_date}/')
		
class RecaudadorExportarMisCobros(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			
			template = get_template('ProyectoApp/historial-recaudaciones.html')

			context = exportar_mis_recaudaciones(request, user_log)

			html = template.render(context)
			pdf = generar_pdf('ProyectoApp/historial-recaudaciones.html', context)
			
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = f'historial_{user_log}.pdf'
				content = f'attachment; filename={filename}'
				response['Content-Disposition'] = content
				return response
			else:
				return HttpResponse('Error')

class RecaudadorFechas(DetailView):
	def get(self, request, user_log, user_filt, tam, th, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			try:
				
				user_log = CustomUser.objects.get(username=user_log)
				form = FormularioFechas()

				context = {
					'user_log': user_log,
					'form': form
				}

				return render(request, 'ProyectoApp/recaudador/recaudador-fechas.html', context)

			except:
				messages.info(request, 'Error')
				return HttpResponseRedirect(f'recaudador/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, user_filt, tam, th, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioFechas(request.POST)

			if form.is_valid():
				
				user_log = CustomUser.objects.get(username=user_log)
				user_filt = CustomUser.objects.get(username=user_filt)

				start_date = form.cleaned_data['fecha1']
				end_date = form.cleaned_data['fecha2']

				if user_filt.groups.filter(name__in=['Recaudador']):
					context = historial_recaud_fechas(request, user_log, user_filt, tam, th, start_date, end_date)

					return render(request, 'ProyectoApp/recaudador/recaudador-historial-recaudador.html', context)

				else:
					context = historial_afil_fechas(request, user_log, user_filt, tam, th, start_date, end_date)

					return render(request, 'ProyectoApp/recaudador/recaudador-ver-historial.html', context)
					
			else:
				messages.error('Error')
				return HttpResponseRedirect(f'recaudador/{user_log}/')

class RecaudadorExportarMisCobrosMes(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			
			template = get_template('ProyectoApp/historial-recaudaciones.html')

			context = exportar_mis_recaudaciones_mes(request, user_log)

			html = template.render(context)
			pdf = generar_pdf('ProyectoApp/historial-recaudaciones.html', context)
			
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = f'historial_mensual{user_log}.pdf'
				content = f'attachment; filename={filename}'
				response['Content-Disposition'] = content
				return response
			else:
				return HttpResponse('Error')

class RecaudadorExportarMisCobrosFechas(DetailView):
	def get(self, request, user_log, start_date, end_date, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			
			template = get_template('ProyectoApp/historial-recaudaciones.html')

			context = exportar_mis_recaudaciones_fechas(request, user_log, start_date, end_date)

			html = template.render(context)
			pdf = generar_pdf('ProyectoApp/historial-recaudaciones.html', context)
			
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = f'historial_fechas{user_log}.pdf'
				content = f'attachment; filename={filename}'
				response['Content-Disposition'] = content
				return response
			else:
				return HttpResponse('Error')

class RecaudadorVerKardex(DetailView):
	def get(self, request, user_log, user_filt, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			
			context = ver_kardex(request, user_log, user_filt)
		
			return render(request, 'ProyectoApp/recaudador/recaudador-ver-kardex.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorActDatos(DetailView):
	''' Vista que permite actualizar todos los datos de los usuarios a excepción de las credenciales '''
	def get(self, request, user_log, user_filt, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			
			user_filt = CustomUser.objects.get(username=user_filt)

			form = FormularioActualizarDatos(
				initial={
				'usuario_vivo': user_filt.usuario_vivo,
				'estado_usuario': user_filt.estado_usuario,
				'matricula': user_filt.matricula,
				'first_name': user_filt.first_name,
				'apell_pat': user_filt.apell_pat,
				'apell_mat': user_filt.apell_mat,
				'lugar_nac': user_filt.lugar_nac,
				'fecha_nac': user_filt.fecha_nac,
				'ci': user_filt.ci,
				'est_civil': user_filt.est_civil,
				'univ_estud': user_filt.univ_estud,
				'fecha_tg': user_filt.fecha_tg,
				'univ_lic': user_filt.univ_lic,
				'fecha_ol': user_filt.fecha_ol,
				'ent_pub': user_filt.ent_pub,
				'fecha_tit_pn': user_filt.fecha_tit_pn,
				'fecha_registro': user_filt.fecha_registro,
				'cargos_judic': user_filt.cargos_judic,
				'cargos_admin_pub': user_filt.cargos_admin_pub,
				'cargos_priv_otras': user_filt.cargos_priv_otras,
				'tiempo_ejec_prof_sd': user_filt.tiempo_ejec_prof_sd,
				'cargo_actual': user_filt.cargo_actual,
				'prod_jur': user_filt.prod_jur,
				'estud_espec': user_filt.estud_espec,
				'recon_obt': user_filt.recon_obt,
				'asist_event_inter': user_filt.asist_event_inter,
				'inst_aseg': user_filt.inst_aseg,
				'beneficiarios': user_filt.beneficiarios,
				'espec_ejer_der': user_filt.espec_ejer_der,
				'direc_ofic': user_filt.direc_ofic,
				'tel_ofic': user_filt.tel_ofic,
				'direcc': user_filt.direcc,
				'telefono': user_filt.telefono,
				'celular': user_filt.celular,
				'email': user_filt.email,
				'observ': user_filt.observ
				}
			)
			es_afiliado = CustomUser.objects.filter(groups__name='Afiliado' ,id = user_filt.id)
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'user_filt': user_filt,
				'form': form,
				"es_afiliado":es_afiliado
				}
			return render(request, 'ProyectoApp/recaudador/recaudador-act-datos.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, user_filt, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			form = FormularioActualizarDatos(request.POST, request.FILES)

			if form.is_valid() and len(form.cleaned_data['matricula'])<=4:
				
				try:
					# Datos a actualizar
					user_mod = CustomUser.objects.get(username=user_filt)
					
					afiliado = CustomUser.objects.filter(groups__name='Afiliado' ,id = user_mod.id)
					if len(afiliado)==0:
						nueva_matricula = str(random.getrandbits(128))
					else:
						nueva_matricula = form.cleaned_data['matricula']
					if form.cleaned_data['foto'] != None:
						user_mod.foto = form.cleaned_data['foto']
						
					user_mod.usuario_vivo = form.cleaned_data['usuario_vivo']
					user_mod.estado_usuario = form.cleaned_data['estado_usuario']
					user_mod.matricula = nueva_matricula,
					user_mod.first_name = form.cleaned_data['first_name'].upper()
					user_mod.apell_pat = form.cleaned_data['apell_pat'].upper()
					user_mod.apell_mat = form.cleaned_data['apell_mat'].upper()
					user_mod.lugar_nac = form.cleaned_data['lugar_nac']
					user_mod.fecha_nac = form.cleaned_data['fecha_nac']
					user_mod.ci = form.cleaned_data['ci']
					user_mod.est_civil = form.cleaned_data['est_civil']
					user_mod.univ_estud = form.cleaned_data['univ_estud']
					user_mod.fecha_tg = form.cleaned_data['fecha_tg']
					user_mod.univ_lic = form.cleaned_data['univ_lic']
					user_mod.fecha_ol = form.cleaned_data['fecha_ol']
					user_mod.ent_pub = form.cleaned_data['ent_pub']
					user_mod.fecha_tit_pn = form.cleaned_data['fecha_tit_pn']
					user_mod.fecha_registro = form.cleaned_data['fecha_registro']
					user_mod.cargos_judic = form.cleaned_data['cargos_judic']
					user_mod.cargos_admin_pub = form.cleaned_data['cargos_admin_pub']
					user_mod.cargos_priv_otras = form.cleaned_data['cargos_priv_otras']
					user_mod.tiempo_ejec_prof_sd = form.cleaned_data['tiempo_ejec_prof_sd']
					user_mod.cargo_actual = form.cleaned_data['cargo_actual']
					user_mod.prod_jur = form.cleaned_data['prod_jur']
					user_mod.estud_espec = form.cleaned_data['estud_espec']
					user_mod.recon_obt = form.cleaned_data['recon_obt']
					user_mod.asist_event_inter = form.cleaned_data['asist_event_inter']
					user_mod.inst_aseg = form.cleaned_data['inst_aseg']
					user_mod.beneficiarios = form.cleaned_data['beneficiarios']
					user_mod.espec_ejer_der = form.cleaned_data['espec_ejer_der']
					user_mod.direc_ofic = form.cleaned_data['direc_ofic']
					user_mod.tel_ofic = form.cleaned_data['tel_ofic']
					user_mod.direcc = form.cleaned_data['direcc']
					user_mod.telefono = form.cleaned_data['telefono']
					user_mod.celular = form.cleaned_data['celular']
					user_mod.email = form.cleaned_data['email']
					user_mod.observ = form.cleaned_data['observ']
					if type(user_mod.matricula) == tuple:
						user_mod.matricula = user_mod.matricula[0]
					user_mod.save()
					
					messages.success(request, '¡Datos actualizados correctamente!')
					return HttpResponseRedirect(f'/recaudverkardex/{user_log}/{user_filt}/')
				
				except Exception as e:
					if str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.matricula':
						messages.error(
							request, f'Ya existe un colegiado con esa matrícula')
						return HttpResponseRedirect(f'/recaudactdatos/{user_log}/{user_filt}/')
						
					elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.ci':
						messages.error(
							request, f'Ya existe un colegiado con ese C.I')
						return HttpResponseRedirect(f'/recaudactdatos/{user_log}/{user_filt}/')
					
					elif str(e) == 'UNIQUE constraint failed: ProyectoApp_customuser.username':
							
							messages.error(request, 'Ya existe un colegiado con ese username')
							return HttpResponseRedirect(f'/recaudactdatos/{user_log}/{user_filt}/')

					else:
						messages.error(request, 'Datos incorrectos')
						
						return HttpResponseRedirect(f'/recaudactdatos/{user_log}/{user_filt}/')
			else:
				messages.error(request, 'Datos no validos!')
				return HttpResponseRedirect(f'/recaudactdatos/{user_log}/{user_filt}/')
				
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorDashboardAfiliadosDeudas(DetailView):
	''' Filtrar a los afiliados que presenten deudas '''
	def get(self, request, user_log, *args, **kwargs):
		print("ENTREEEE AQUIII")
		if request.user.groups.filter(name__in=['Recaudador']):
			
			afiliados_deudas = generar_info_direc_afiliados_deudas(request, user_log)
			
			fact_emit_total = 0
			fact_paga_total = 0
			fact_venc_total = 0
			deuda_total = 0

			for afiliado in afiliados_deudas:
				fact_emit_total += afiliado['fact_emitidas']

			for afiliado in afiliados_deudas:
				fact_paga_total += afiliado['fact_pagadas']

			for afiliado in afiliados_deudas:
				fact_venc_total += afiliado['fact_vencidas']

			for afiliado in afiliados_deudas:
				deuda_total += afiliado['deuda']

			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'afiliados_deudas': afiliados_deudas,
				'fact_emit_total': fact_emit_total,
				'fact_paga_total': fact_paga_total,
				'fact_venc_total': fact_venc_total,
				'deuda_total': deuda_total

			}

			return render(request, 'ProyectoApp/recaudador/recaudador-dashboard-afiliados-deudas.html', context)
		
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudEsteMes(DetailView):
	''' Información relacionada a recaudaciones este mes '''
	def get(self, request, user_log, tam, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo', 'Recaudador']):
			user_log = CustomUser.objects.get(username=user_log)  # Directivo/Recaudador

			
			if user_log.groups.filter(name__in=['Directivo']):
				
				context = recaud_mes(request, user_log, tam)

				return render(request, 'ProyectoApp/directivo/directivo-reporte-recaud.html', context)
			
			else:
				context = recaud_mes(request, user_log, tam)

				return render(request, 'ProyectoApp/recaudador/recaudador-reporte-recaud.html', context)

		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class ReporteAnual(DetailView):
	''' Información relacionada a recaudaciones por año '''
	def get(self, request, user_log, tam, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo', 'Recaudador']):
			
			user_log = CustomUser.objects.get(username=user_log)  # Directivo/Recaudador
			form = FormularioYear()
			
			if user_log.groups.filter(name__in=['Directivo']):
				
				context = {
					'user_log': user_log,
					'form': form
				}

				return render(request, 'ProyectoApp/directivo/directivo-year.html', context)

			else:
				
				context = {
					'user_log': user_log,
					'form': form
				}

				return render(request, 'ProyectoApp/recaudador/recaudador-year.html', context)

		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, tam, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo', 'Recaudador']):
			
			user_log = CustomUser.objects.get(username=user_log)  # Directivo/Recaudador
			form = FormularioYear(request.POST)
			
			if user_log.groups.filter(name__in=['Directivo']):
				
				if form.is_valid():

					year = form.cleaned_data['year']
					
					start_date = datetime.date(int(year), 1, 1)
					end_date = datetime.date(int(year), 12, 31)
					
					context = reporte_fechas(request, user_log, tam, start_date, end_date)

					return render(request, 'ProyectoApp/directivo/directivo-reporte-recaud.html', context)

				else:
					messages.error('No se ha podido procesar recaudaciones para el año seleccionado')
					return HttpResponseRedirect(f'/directivo{user_log}/')
			else:
				
				if form.is_valid():

					year = form.cleaned_data['year']
					
					start_date = datetime.date(int(year), 1, 1)
					end_date = datetime.date(int(year), 12, 31)

					context = reporte_fechas(request, user_log, tam, start_date, end_date)

					return render(request, 'ProyectoApp/recaudador/recaudador-reporte-recaud.html', context)

				else:
					messages.error('No se ha podido procesar recaudaciones para el año seleccionado')
					return HttpResponseRedirect(f'/recaudador/{user_log}/')

		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class ReporteFechas(DetailView):
	''' Información relacionada a recaudaciones entre fechas '''
	def get(self, request, user_log, tam, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo', 'Recaudador']):
			
			user_log = CustomUser.objects.get(username=user_log)  # Directivo/Recaudador
			form = FormularioFechas()
			
			if user_log.groups.filter(name__in=['Directivo']):
				
				context = {
					'user_log': user_log,
					'form': form
				}

				return render(request, 'ProyectoApp/directivo/directivo-fechas.html', context)

			
			else:
				
				context = {
					'user_log': user_log,
					'form': form
				}

				return render(request, 'ProyectoApp/recaudador/recaudador-fechas.html', context)

		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, tam, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo', 'Recaudador']):
			
			user_log = CustomUser.objects.get(username=user_log)  # Directivo/Recaudador
			form = FormularioFechas(request.POST)
			
			if user_log.groups.filter(name__in=['Directivo']):
				
				if form.is_valid():

					start_date = form.cleaned_data['fecha1']
					end_date = form.cleaned_data['fecha2']

					context = reporte_fechas(request, user_log, tam, start_date, end_date)

					return render(request, 'ProyectoApp/directivo/directivo-reporte-recaud.html', context)

				else:
					messages.error('No se ha podido procesar recaudaciones entre las fechas estipuladas')
					return HttpResponseRedirect(f'/directivo{user_log}/')
			else:
				
				if form.is_valid():

					start_date = form.cleaned_data['fecha1']
					end_date = form.cleaned_data['fecha2']

					context = reporte_fechas(request, user_log, tam, start_date, end_date)

					return render(request, 'ProyectoApp/recaudador/recaudador-reporte-recaud.html', context)

				else:
					messages.error('No se ha podido procesar recaudaciones entre las fechas estipuladas')
					return HttpResponseRedirect(f'/recaudador/{user_log}/')

		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class ReporteFechasListo(DetailView):
	def get(self, request, user_log, tam, start_date, end_date, *args, **kwargs):
		if request.user.groups.filter(name__in=['Directivo', 'Recaudador']):
			
			user_log = CustomUser.objects.get(username=user_log)

			context = reporte_fechas(request, user_log, tam, start_date, end_date)

			if user_log.groups.filter(name__in=['Directivo']):

				return render(request, 'ProyectoApp/directivo/directivo-reporte-recaud.html', context)

			else:
				return render(request, 'ProyectoApp/recaudador/recaudador-reporte-recaud.html', context)

		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class RecaudadorEliminarUsuario(DetailView):
	def get(self, request, user_log, usuario, *args, **kwargs):
		if request.user.groups.filter(name__in=['Recaudador']):
			
			user_log = CustomUser.objects.get(username=user_log)
			
			usuario = CustomUser.objects.get(username=usuario)  # Usuario a eliminar
			usuario.delete()

			messages.success(request, f'El usuario {usuario.username} ha sido eliminado satisfactoriamente')
			return HttpResponseRedirect(f'/recaudador/{user_log}/')
		
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

# ---------------------------------------- VISTAS PARA AFILIADOS ------------------------------------------------

class AfiliadoBienvenida(ListView):
	''' Ventana de bienvenida cada vez que un Afiliado ingresa al sitio web '''
	def get(self, request, *args, **kwargs):
		if request.user.groups.filter(name__in=['Afiliado']):
			user_log = CustomUser.objects.get(username=request.user)
		
			context = {
				'user_log': user_log
			}

			return render(request, 'ProyectoApp/afiliado/afiliado-bienvenida.html', context)

class AfiliadoDashboard(DetailView):
	''' Información relacionada a su rol de Afiliado '''
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Afiliado']):
			
			context = generar_info_afil(request, user_log)  # Carga toda su información
			
			return render(request, 'ProyectoApp/afiliado/afiliado-dashboard.html', context)

class AfiliadoVerMiKardex(DetailView):
	def get(self, request, user_log, *args, **kwargs):

		if request.user.groups.filter(name__in=['Afiliado']):

			context = {
				'user_log': CustomUser.objects.get(username=user_log)
			}
			
			return render(request, 'ProyectoApp/afiliado/afiliado-ver-mi-kardex.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class AfiliadoHistorial(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Afiliado']):
			
			context = generar_historial_afil(request, user_log)

			try:
				return render(request, 'ProyectoApp/afiliado/afiliado-historial.html', context)

			except:
				return HttpResponse('No tienes historial de aportes')

class AfiliadoHistorialFiltrado(DetailView):
	def get(self, request, user_log, ta, *args, **kwargs):
		if request.user.groups.filter(name__in=['Afiliado']):
			context = generar_historial_afil_fil(request, user_log, ta)

			try:
				return render(request, 'ProyectoApp/afiliado/afiliado-historial-filtrado.html', context)

			except:
				return HttpResponse('No tienes historial para ese tipo de aportes')

class AfiliadoModClave(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Afiliado']):
			
			aporte_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')
			aporte_inicial = AporteMensual.objects.get(aporte_mensual_deno='AMI')

			form = FormularioModificarClave()
			context = {
				'user_log': CustomUser.objects.get(username=user_log),
				'form': form,
				'aporte_actual': aporte_actual,
				'aporte_inicial': aporte_inicial
				}
			return render(request, 'ProyectoApp/afiliado/afiliado-mod-clave.html', context)

	def post(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Afiliado']):
			form = FormularioModificarClave(request.POST)

			if form.is_valid():
				
				if form.cleaned_data['password1'] == form.cleaned_data['password2']:
					
					afiliado = CustomUser.objects.get(username=user_log)
					
					if afiliado.check_password(form.cleaned_data['password1']):
						
						if form.cleaned_data['password_new1'] == form.cleaned_data['password_new2']:
					
							afiliado.password = make_password(
										form.cleaned_data['password_new1'],
										salt=None,
										hasher='default'
									)
								
							afiliado.save()

							messages.success(request, 'Clave modificada satisfactoriamente')
							return HttpResponseRedirect(f'/afiliado-bienvenida/{user_log}/')

						else:
							messages.error(request, 'Las claves a cambiar no coinciden')
							return HttpResponseRedirect(f'/afiliadomodclave/{user_log}/')

					else:
						messages.error(request, 'Error en la verificación de tu clave')
						return HttpResponseRedirect(f'/afiliadomodclave/{user_log}/')

				else:
					messages.error(request, 'Las claves actuales no coinciden')
					return HttpResponseRedirect(f'/afiliadomodclave/{user_log}/')

			else:
				messages.error(request, 'Datos introducidos incorrectamente')
				return HttpResponseRedirect(f'/afiliadomodclave/{user_log}/')
										
class AfiliadoDetalles(DetailView):
	def get(self, request, user_log, comprobante, *args, **kwargs):
		if request.user.groups.filter(name__in=['Afiliado']):
			user_log = CustomUser.objects.get(username=user_log)
			info = AporteAfiliado.objects.get(comprobante=comprobante)
			aporte_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')
			aporte_inicial = AporteMensual.objects.get(aporte_mensual_deno='AMI')
			
			context = {
				'user_log': user_log,
				'info': info,
				'aporte_actual': aporte_actual,
				'aporte_inicial': aporte_inicial
			}

			return render(request, 'ProyectoApp/afiliado/afiliado-detalles.html', context)

class AfiliadoVerHistorial(DetailView):
	def get(self, request, user_log, tam, th, start_date, end_date, *args, **kwargs):
		if request.user.groups.filter(name__in=['Afiliado']):
			try:
				
				context = cal_deuda_afiliado(request, user_log, tam, th, start_date, end_date)

				return render(request, 'ProyectoApp/afiliado/afiliado-ver-historial.html', context)

			except Exception as e:
				messages.info(request, 'No tienes registro de aportes mensuales')
				return HttpResponseRedirect(f'/afiliado-bienvenida/{user_log}/')

class AfiliadoExportarHistorial(DetailView):
	def get(self, request, user_log, tam, th, start_date, end_date, *args, **kwargs):
		if request.user.groups.filter(name__in=['Afiliado']):
			
			template = get_template('ProyectoApp/historial-afiliado.html')

			context = exportar_historial_afil(request, user_log, tam, th, start_date, end_date)

			html = template.render(context)
			pdf = generar_pdf('ProyectoApp/historial-afiliado.html', context)
			
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = f'historial_{user_log}.pdf'
				content = f'attachment; filename={filename}'
				response['Content-Disposition'] = content
				return response
			else:
				return HttpResponse('Error')


class AfiliadoInfo(DetailView):
	def get(self, request, user_log, *args, **kwargs):
		if request.user.groups.filter(name__in=['Afiliado']):
			
			context = cal_deuda(request, user_log, user_log, 'AMU')
		
			return render(request, 'ProyectoApp/afiliado/afiliado-info.html', context)
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

class AfiliadoFechas(DetailView):
	def get(self, request, user_log, tam, th, *args, **kwargs):
		if request.user.groups.filter(name__in=['Afiliado']):
			try:
				
				aporte_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')
				aporte_inicial = AporteMensual.objects.get(aporte_mensual_deno='AMI')

				user_log = CustomUser.objects.get(username=user_log)
				form = FormularioFechas()

				context = {
					'user_log': user_log,
					'form': form,
					'aporte_actual': aporte_actual,
					'aporte_inicial': aporte_inicial
				}

				return render(request, 'ProyectoApp/afiliado/afiliado-fechas.html', context)

			except:
				messages.info(request, 'Error')
				return HttpResponseRedirect(f'afiliado-bienvenida/{user_log}/')
		else:
			return HttpResponse('No tienes permiso para acceder a esta sección')

	def post(self, request, user_log, tam, th, *args, **kwargs):
		if request.user.groups.filter(name__in=['Afiliado']):
			form = FormularioFechas(request.POST)

			if form.is_valid():
				
				user_log = CustomUser.objects.get(username=user_log)
			
				start_date = form.cleaned_data['fecha1']
				end_date = form.cleaned_data['fecha2']

				context = cal_deuda_afiliado(request, user_log, tam, th, start_date, end_date)

				return render(request, 'ProyectoApp/afiliado/afiliado-ver-historial.html', context)

			else:
				messages.error('Error')
				return HttpResponseRedirect(f'/afiliado-bienvenida/{user_log}/')

# -------------------------------------- VISTAS COMPARTIDAS -----------------------------------------------------
class EliminarAporte(DetailView):
	''' ELIMINAR APORTES DE ACUERDO A N° DE COMPROBANTE '''

	def get(self, request, user_log, comprobante, *args, **kwargs):
		
		if request.user.groups.filter(name__in=['Directivo', 'Recaudador']):
			
			user_log = CustomUser.objects.get(username=user_log)  # Directivo/Recaudador
			
			aporte = AporteAfiliado.objects.get(comprobante=comprobante)
			aporte.delete()

			messages.success(request, 'Se ha eliminado satisfactoriamente el aporte')

			if user_log.groups.filter(name__in=['Directivo']):
				return HttpResponseRedirect(f'/directivo{user_log}/')
			else:
				return HttpResponseRedirect(f'/recaudador/{user_log}/')

		else:
			return HttpResponse('No tienes permiso para eliminar aportes')

class EnviarComprobante(DetailView):
	def get(self, request, comprobante):

		try:

			x = enviar_comprobante(request, comprobante)

			if x == 1:
				messages.success(request, 'Se ha enviado el comprobante correctamente')
				return HttpResponseRedirect(f'/recaudadorcobroefectuado/{request.user}/{comprobante}/')
			
			else:
				messages.error(request, f'No se ha podido enviar el comprobante {x}')
				return HttpResponseRedirect(f'/recaudadorcobroefectuado/{request.user}/{comprobante}/')

		except Exception as e:
			messages.error(request, f'No se ha podido enviar el comprobante')
			return HttpResponseRedirect(f'/recaudadorcobroefectuado/{request.user}/{comprobante}/')

class GenerarPDF(DetailView):
	def get(self, request, comprobante, *args, **kwargs):

		template = get_template('ProyectoApp/comprobante.html')

		info_aporte = AporteAfiliado.objects.get(comprobante=comprobante)
		recaudador = CustomUser.objects.get(username=info_aporte.recaudador)
		querie = Fechas.objects.get(id=info_aporte.fecha_id_pago_id)
		
		if info_aporte.aporte_mensual_afil != None:
			monto = info_aporte.aporte_mensual_afil.aporte_mensual
			etiqueta = 'Aporte Mensual'
		
		elif info_aporte.aporte_certif_afil != None:
			monto = info_aporte.aporte_certif_afil.aporte_certificacion
			etiqueta = 'Aporte por Certificación'

		else:
			monto = info_aporte.aporte_dona_afil
			etiqueta = 'Aporte por donación'

		context = {	
			# INFORMACIÓN DEL APORTE
			'comprobante': info_aporte.comprobante,
			'talonario': info_aporte.talonario,
			'etiqueta': etiqueta,
			'monto': monto,
			'fecha_pago': info_aporte.fecha_pago,
			# DATOS DEL AFILIADO
			'afiliado': info_aporte.afiliado,
			'afiliado_ci': info_aporte.afiliado.ci,
			'afiliado_mat': info_aporte.afiliado.matricula,
			# DATOS DEL RECAUDADOR
			'recaudador': recaudador.username,
			'recaudador_ci': recaudador.ci,
			'recaudador_mat': recaudador.matricula,
			'mes_pagado': str(querie.agno) + "-" + str(querie.mes_abreviado),
			'numero_recibo':info_aporte.numero_recibo,
			'recaudador_apell_pat':recaudador.apell_pat,
			'recaudador_first_name':recaudador.first_name
		}

		html = template.render(context)
		pdf = generar_pdf('ProyectoApp/comprobante.html', context)
		
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			filename = f'comprobante_{info_aporte.fecha_pago}.pdf'
			content = f'attachment; filename={filename}'
			response['Content-Disposition'] = content
			return response
		else:
			return HttpResponse('No válido')

class ImprimirKardex(DetailView):
	def get(self, request, user_filt, *args, **kwargs):

		template = get_template('ProyectoApp/imprimir-kardex.html')

		user_filt = CustomUser.objects.get(username=user_filt)

		context = {	
			'user_filt': user_filt,
		}

		html = template.render(context)
		pdf = generar_pdf('ProyectoApp/imprimir-kardex.html', context)
		
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			filename = f'Kardex_{user_filt.username}.pdf'
			content = f'attachment; filename={filename}'
			response['Content-Disposition'] = content
			return response
		else:
			return HttpResponse('Not valid')

class ExportarAfiliadosDeudores(DetailView):
	def get(self, request, user_log, *args, **kwargs):

		template = get_template('ProyectoApp/historial-afiliados-deudas.html')

		afiliados_deudas = generar_info_direc_afiliados_deudas(request, user_log)
			
		fact_emit_total = 0
		fact_paga_total = 0
		fact_venc_total = 0
		deuda_total = 0

		for afiliado in afiliados_deudas:
			fact_emit_total += afiliado['fact_emitidas']

		for afiliado in afiliados_deudas:
			fact_paga_total += afiliado['fact_pagadas']

		for afiliado in afiliados_deudas:
			fact_venc_total += afiliado['fact_vencidas']

		for afiliado in afiliados_deudas:
			deuda_total += afiliado['deuda']

		context = {
			'user_log': CustomUser.objects.get(username=user_log),
			'afiliados_deudas': afiliados_deudas,
			'fact_emit_total': fact_emit_total,
			'fact_paga_total': fact_paga_total,
			'fact_venc_total': fact_venc_total,
			'deuda_total': deuda_total
		}

		html = template.render(context)
		pdf = generar_pdf('ProyectoApp/historial-afiliados-deudas.html', context)
		
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			filename = f'Reporte_Colegiados_deudores.pdf'
			content = f'attachment; filename={filename}'
			response['Content-Disposition'] = content
			return response
		else:
			return HttpResponse('Not valid')


def validar_matricula(matricula):
		validation  =False
		if len(matricula) == 0:
    			return validation
				
		if len(matricula) >4:
    			return validation

		validation = True
		return validation