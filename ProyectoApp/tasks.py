# DJANGO
from django.core.paginator import Paginator
from django.utils import timezone
from Proyecto.settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.template.loader import get_template
from django.http import HttpResponse
from datetime import date
from dateutil import rrule
# MÓDULOS EXTERNOSs
from xhtml2pdf import pisa
import io
import datetime

# PERTENECIENTES AL PROYECTO
from .models import CustomUser, AporteAfiliado, AporteMensual, AporteCertificacion,Fechas

def cal_deuda(request, user_log, user_filt, tam):

	aporte_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	aporte_inicial = AporteMensual.objects.get(aporte_mensual_deno='AMI')

	if tam == 'AMU':

		try:
			user_log = CustomUser.objects.get(username=user_log)  # Directivo/Recaudador
			user_filt = CustomUser.objects.get(username=user_filt)  # Afiliado

			# FACTURAS POR APORTES MENSUALES
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
			
			# Fecha de inicio de cobros mensuales
			fecha_inicio = user_filt.fecha_registro

			fact_emitidas = int((datetime.datetime.now().date() - fecha_inicio).days / 30)	
			if fact_emitidas <= 0:
				fact_emitidas = 1
			else:
				fact_emitidas+=1

			historial = AporteAfiliado.objects.filter(
									afiliado=user_filt.id,
									aporte_mensual_afil=tipo_factura.id,
									).order_by('-fecha_pago')
					
			fact_pagadas = len(historial)
			fact_vencidas = sum([fact_emitidas, -fact_pagadas])

			deuda = fact_vencidas * int(tipo_factura.aporte_mensual)
			total_aportado = fact_pagadas * int(tipo_factura.aporte_mensual)

			paginator = Paginator(historial, 10)  # Mostrará hasta 5 historial por pág.
			page = request.GET.get('page')
			historial = paginator.get_page(page)

			context = {
				'user_log': user_log,
				'tipo_factura': tipo_factura,
				'user_filt': user_filt,
				'historial': historial,
				'fact_emitidas': fact_emitidas,
				'fact_pagadas': fact_pagadas,
				'fact_pendientes': fact_emitidas - fact_pagadas,
				'deuda': deuda,
				'total_aportado': total_aportado,
				'AMU': True,
				'aporte_actual': aporte_actual,
				'aporte_inicial': aporte_inicial
			}

			return context

		except Exception as e:

			user_log = CustomUser.objects.get(username=user_log)

			context = {
				'user_log': user_log,
				'aporte_actual': aporte_actual,
				'aporte_inicial': aporte_inicial
				}

			return context

	else:
		try:
			user_log = CustomUser.objects.get(username=user_log)  # Directivo/Recaudador
			user_filt = CustomUser.objects.get(username=user_filt)  # Afiliado

			# FACTURAS POR APORTES MENSUALES
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
			
			tipo_factura_nueva = AporteMensual.objects.get(aporte_mensual_deno='AMU')

			# Fecha de inicio de cobros mensuales
			fecha_inicio = tipo_factura.fecha_inicio_cobros
			fecha_final = tipo_factura_nueva.fecha_inicio_cobros

			fact_emitidas = int((fecha_final - fecha_inicio).days / 30)	
			
			historial = AporteAfiliado.objects.filter(
									afiliado=user_filt.id,
									aporte_mensual_afil=tipo_factura.id,
									).order_by('-fecha_pago')
			
			fact_pagadas = len(historial)
			fact_vencidas = sum([fact_emitidas, -fact_pagadas])

			deuda = fact_vencidas * int(tipo_factura.aporte_mensual)
			total_aportado = fact_pagadas * int(tipo_factura.aporte_mensual)

			paginator = Paginator(historial, 10)  # Mostrará hasta 10 historial por pág.
			page = request.GET.get('page')
			historial = paginator.get_page(page)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'tipo_factura': tipo_factura,
				'historial': historial,
				'fact_emitidas': fact_emitidas,
				'fact_pagadas': fact_pagadas,
				'fact_pendientes': fact_emitidas - fact_pagadas,
				'deuda': deuda,
				'total_aportado': total_aportado,
				'estado': user_filt.estado_usuario,
				'AMI': True,
				'aporte_actual': aporte_actual,
				'aporte_inicial': aporte_inicial
			}

			return context

		except Exception as e:

			user_log = CustomUser.objects.get(username=user_log)

			context = {
				'user_log': user_log,
				'aporte_actual': aporte_actual,
				'aporte_inicial': aporte_inicial
			}

			return context

def cal_deuda_afiliado(request, user_log, tam, th, start_date, end_date):
	user_log = CustomUser.objects.get(username=user_log)  # Afiliado
	aporte_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	aporte_inicial = AporteMensual.objects.get(aporte_mensual_deno='AMI')


	if tam == 'AMU' and th == 'TODO' and start_date == 'None' and end_date == 'None':

		# FACTURAS POR APORTES MENSUALES
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno=tam)
		
		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id
								).order_by('-fecha_pago')

		# Fecha de inicio de cobros mensuales
		fecha_inicio = user_log.fecha_registro
		fact_emitidas = int((datetime.datetime.now().date() - fecha_inicio).days / 30)	
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1
		
		fact_pagadas = len(historial)
		fact_vencidas = fact_emitidas - fact_pagadas

		deuda = fact_vencidas * int(tipo_factura.aporte_mensual)
		total_aportado = fact_pagadas * int(tipo_factura.aporte_mensual)

		paginator = Paginator(historial, 10)  # Mostrará hasta 10 historial por pág.
		page = request.GET.get('page')
		historial = paginator.get_page(page)

		context = {
			'user_log': user_log,
			'historial': historial,
			'todo': False,
			'mes': False,
			'fechas': False,
			'fact_emitidas': fact_emitidas,
			'fact_pagadas': fact_pagadas,
			'fact_pendientes': sum([fact_emitidas, -fact_pagadas]),
			'deuda': deuda,
			'total_aportado': total_aportado,
			'estado': user_log.estado_usuario,
			'monto_unit': tipo_factura.aporte_mensual,
			'tam': tam,
			'th': th,
			'start_date': start_date,
			'end_date': end_date,
			'aporte_actual': aporte_actual,
			'aporte_inicial': aporte_inicial
		}

	
	elif tam == 'AMI' and th == 'TODO' and start_date == 'None' and end_date == 'None':
		# FACTURAS POR APORTES MENSUALES
		tipo_factura_inicial = AporteMensual.objects.get(aporte_mensual_deno=tam)
		tipo_factura_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')

		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura_inicial.id
								).order_by('-fecha_pago')

		# Fecha de inicio de cobros mensuales
		fecha_inicio = tipo_factura_inicial.fecha_inicio_cobros
		fecha_final = tipo_factura_actual.fecha_inicio_cobros

		fact_emitidas = int((fecha_final - fecha_inicio).days / 30)	
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1
		
		cant_aportes = len(historial)
		fact_vencidas = sum([fact_emitidas, -cant_aportes])

		deuda = fact_vencidas * int(tipo_factura_inicial.aporte_mensual)
		
		paginator = Paginator(historial, 10)  # Mostrará hasta 10 historial por pág.
		page = request.GET.get('page')
		historial = paginator.get_page(page)

		context = {
			'user_log': user_log,
			'historial': historial,
			'todo': False,
			'mes': False,
			'cant_aportes': cant_aportes,
			'fechas': False,
			'fact_emitidas': fact_emitidas,
			'fact_pendientes': sum([fact_emitidas, -cant_aportes]),
			'deuda': deuda,
			'total_aportado': cant_aportes * int(tipo_factura_inicial.aporte_mensual),
			'estado': user_log.estado_usuario,
			'monto_unit': tipo_factura_inicial.aporte_mensual,
			'tam': tam,
			'th': th,
			'start_date': start_date,
			'end_date': end_date,
			'aporte_actual': aporte_actual,
			'aporte_inicial': aporte_inicial
		}

	

	elif tam == 'AMU' and th == 'MES' and start_date == 'None' and end_date == 'None':
		# FACTURAS POR APORTES MENSUALES
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno=tam)
		start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
		end_date = datetime.datetime.now().date()  # Fecha actual
		
		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id,
								).order_by('-fecha_pago')

		# Fecha de inicio de cobros mensuales
		fecha_inicio = user_log.fecha_registro
		fact_emitidas = int((datetime.datetime.now().date() - fecha_inicio).days / 30)	
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1
			
		fact_pagadas = len(historial)
		fact_vencidas = sum([fact_emitidas, -fact_pagadas])

		deuda = fact_vencidas * int(tipo_factura.aporte_mensual)
		total_aportado = fact_pagadas * int(tipo_factura.aporte_mensual)

		historial = AporteAfiliado.objects.filter(
							afiliado=user_log.id,
							aporte_mensual_afil=tipo_factura.id,
							fecha_pago__range=[start_date, end_date]
							).order_by('-fecha_pago')

		paginator = Paginator(historial, 10)  # Mostrará hasta 10 historial por pág.
		page = request.GET.get('page')
		historial = paginator.get_page(page)

		context = {
			'user_log': user_log,
			'historial': historial,
			'todo': True,
			'mes': True,
			'fechas': False,
			'fact_emitidas': fact_emitidas,
			'fact_pagadas': fact_pagadas,
			'fact_pendientes': sum([fact_emitidas, -fact_pagadas]),
			'deuda': deuda,
			'total_aportado': total_aportado,
			'estado': user_log.estado_usuario,
			'monto_unit': tipo_factura.aporte_mensual,
			'tam': tam,
			'th': th,
			'start_date': 'None',
			'end_date': 'None',
			'aporte_actual': aporte_actual,
			'aporte_inicial': aporte_inicial
		}

	elif tam == 'AMI' and th == 'MES' and start_date == 'None' and end_date == 'None':
		# FACTURAS POR APORTES MENSUALES
		start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
		end_date = datetime.datetime.now().date()  # Fecha actual
		
		# FACTURAS POR APORTES MENSUALES
		tipo_factura_inicial = AporteMensual.objects.get(aporte_mensual_deno=tam)
		tipo_factura_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')

		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura_inicial.id,
								).order_by('-fecha_pago')

		# Fecha de inicio de cobros mensuales
		fecha_inicio = tipo_factura_inicial.fecha_inicio_cobros
		fecha_final = tipo_factura_actual.fecha_inicio_cobros

		fact_emitidas = int((fecha_final - fecha_inicio).days / 30)	
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1
		
		cant_aportes = len(historial)
		fact_vencidas = sum([fact_emitidas, -cant_aportes])

		deuda = fact_vencidas * int(tipo_factura_inicial.aporte_mensual)
		
		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura_inicial.id,
								fecha_pago__range=[start_date, end_date]
								).order_by('-fecha_pago')

		paginator = Paginator(historial, 10)  # Mostrará hasta 10 historial por pág.
		page = request.GET.get('page')
		historial = paginator.get_page(page)

		context = {
			'user_log': user_log,
			'historial': historial,
			'todo': False,
			'mes': False,
			'cant_aportes': cant_aportes,
			'fechas': False,
			'fact_emitidas': fact_emitidas,
			'fact_pendientes': sum([fact_emitidas, -cant_aportes]),
			'deuda': deuda,
			'total_aportado': cant_aportes * int(tipo_factura_inicial.aporte_mensual),
			'estado': user_log.estado_usuario,
			'monto_unit': tipo_factura_inicial.aporte_mensual,
			'tam': tam,
			'th': th,
			'start_date': 'None',
			'end_date': 'None',
			'aporte_actual': aporte_actual,
			'aporte_inicial': aporte_inicial
		}

	 

	elif tam == 'AMU' and th == 'FECHAS' and start_date != 'None' and end_date != 'None':
		# FACTURAS POR APORTES MENSUALES
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno=tam)
		
		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id,
								).order_by('-fecha_pago')

		# Fecha de inicio de cobros mensuales
		fecha_inicio = user_log.fecha_registro
		fact_emitidas = int((datetime.datetime.now().date() - fecha_inicio).days / 30)	
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1
	
		fact_pagadas = len(historial)
		fact_vencidas = sum([fact_emitidas, -fact_pagadas])

		deuda = fact_vencidas * int(tipo_factura.aporte_mensual)
		total_aportado = fact_pagadas * int(tipo_factura.aporte_mensual)

		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id,
								fecha_pago__range=[start_date, end_date]
								).order_by('-fecha_pago')

		paginator = Paginator(historial, 10)  # Mostrará hasta 10 historial por pág.
		page = request.GET.get('page')
		historial = paginator.get_page(page)

		context = {
			'user_log': user_log,
			'historial': historial,
			'todo': False,
			'mes': False,
			'fechas': False,
			'fact_emitidas': fact_emitidas,
			'fact_pagadas': fact_pagadas,
			'fact_pendientes': sum([fact_emitidas, -fact_pagadas]),
			'deuda': deuda,
			'total_aportado': total_aportado,
			'estado': user_log.estado_usuario,
			'monto_unit': tipo_factura.aporte_mensual,
			'tam': tam,
			'th': th,
			'start_date': start_date,
			'end_date': end_date,
			'aporte_actual': aporte_actual,
			'aporte_inicial': aporte_inicial
		}

	

	else:
		# FACTURAS POR APORTES MENSUALES
		tipo_factura_inicial = AporteMensual.objects.get(aporte_mensual_deno=tam)
		tipo_factura_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')

		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura_inicial.id,
								).order_by('-fecha_pago')

		# Fecha de inicio de cobros mensuales
		fecha_inicio = tipo_factura_inicial.fecha_inicio_cobros
		fecha_final = tipo_factura_actual.fecha_inicio_cobros

		fact_emitidas = int((fecha_final - fecha_inicio).days / 30)	
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1
		
		cant_aportes = len(historial)
		fact_vencidas = sum([fact_emitidas, -cant_aportes])

		deuda = fact_vencidas * int(tipo_factura_inicial.aporte_mensual)
		
		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura_inicial.id,
								fecha_pago__range=[start_date, end_date]
								).order_by('-fecha_pago')

		paginator = Paginator(historial, 10)  # Mostrará hasta 10 historial por pág.
		page = request.GET.get('page')
		historial = paginator.get_page(page)

		context = {
			'user_log': user_log,
			'historial': historial,
			'todo': False,
			'mes': False,
			'cant_aportes': cant_aportes,
			'fechas': False,
			'fact_emitidas': fact_emitidas,
			'fact_pendientes': sum([fact_emitidas, -cant_aportes]),
			'deuda': deuda,
			'total_aportado': cant_aportes * int(tipo_factura_inicial.aporte_mensual),
			'estado': user_log.estado_usuario,
			'monto_unit': tipo_factura_inicial.aporte_mensual,
			'tam': tam,
			'th': th,
			'start_date': start_date,
			'end_date': end_date,
			'aporte_actual': aporte_actual,
			'aporte_inicial': aporte_inicial
		}

	return context  

def cal_deuda_afiliado_simple(user_filt):

	user_filt = CustomUser.objects.get(username=user_filt)  # Afiliado
	fact_ami = AporteMensual.objects.get(aporte_mensual_deno='AMI')
	fact_amu = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	
	aportes_ami = AporteAfiliado.objects.filter(
						afiliado=user_filt.id,
						aporte_mensual_afil=fact_ami.id
						).order_by('-fecha_pago')

	aportes_amu = AporteAfiliado.objects.filter(
						afiliado=user_filt.id,
						aporte_mensual_afil=fact_amu.id
						).order_by('-fecha_pago')

	if len(aportes_ami) == 0:
		
		# APORTES ACTUALES
		fecha_inicio = user_filt.fecha_registro

		fact_emitidas = int((datetime.datetime.now().date() - fecha_inicio).days / 30)	
		
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1

		historial = AporteAfiliado.objects.filter(
								afiliado=user_filt.id,
								aporte_mensual_afil=fact_amu.id
								).order_by('-fecha_pago')
	
		fact_pagadas = len(historial)
		fact_vencidas = fact_emitidas - fact_pagadas

		deuda = fact_vencidas * int(fact_amu.aporte_mensual)
		total_aportado = fact_pagadas * int(fact_amu.aporte_mensual)

		context = {
			# AMI
			'fact_emitidas_ami': 0,
			'fact_pagadas_ami': 0,
			'fact_pendientes_ami': 0,
			'deuda_ami': 0,
			'total_aportado_ami': 0,
			'fact_vencidas_ami': 0,

			# AMU
			'fact_emitidas': fact_emitidas,
			'fact_pagadas': fact_pagadas,
			'fact_pendientes': sum([fact_emitidas, -fact_pagadas]),
			'deuda': deuda,
			'total_aportado': total_aportado,
			'fact_vencidas': fact_vencidas,
			
			'estado': user_filt.estado_usuario,
			'AMU': True,
			'AMI': False
		}

	else:
		
		# APORTES INICIALES
		fecha_inicio = fact_ami.fecha_inicio_cobros
		fecha_fin = fact_amu.fecha_inicio_cobros

		fact_emitidas_ami = int((fecha_fin - fecha_inicio).days / 30)	
		
		if fact_emitidas_ami <= 0:
			fact_emitidas_ami = 1

		historial = AporteAfiliado.objects.filter(
								afiliado=user_filt.id,
								aporte_mensual_afil=fact_ami.id
								).order_by('-fecha_pago')
	
		fact_pagadas_ami = len(historial)
		fact_vencidas_ami = sum([fact_emitidas_ami, -fact_pagadas_ami])

		deuda_ami = fact_vencidas_ami * int(fact_ami.aporte_mensual)
		total_aportado_ami = fact_pagadas_ami * int(fact_ami.aporte_mensual)

		# APORTES ACTUALES
		fecha_inicio = user_filt.fecha_registro

		fact_emitidas = int((datetime.datetime.now().date() - fecha_inicio).days / 30)	
		
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1

		historial = AporteAfiliado.objects.filter(
								afiliado=user_filt.id,
								aporte_mensual_afil=fact_amu.id
								).order_by('-fecha_pago')
	
		fact_pagadas = len(historial)
		fact_vencidas = sum([fact_emitidas, -fact_pagadas])

		deuda = fact_vencidas * int(fact_amu.aporte_mensual)
		total_aportado = fact_pagadas * int(fact_amu.aporte_mensual)

		context = {
			# AMI
			'fact_emitidas_ami': fact_emitidas_ami,
			'fact_pagadas_ami': fact_pagadas_ami,
			'fact_pendientes_ami': sum([fact_emitidas_ami, -fact_pagadas_ami]),
			'deuda_ami': deuda_ami,
			'total_aportado_ami': total_aportado_ami,
			'fact_vencidas_ami': fact_vencidas_ami,

			# AMU
			'fact_emitidas': fact_emitidas,
			'fact_pagadas': fact_pagadas,
			'fact_pendientes': sum([fact_emitidas, -fact_pagadas]),
			'deuda': deuda,
			'total_aportado': total_aportado,
			'fact_vencidas': fact_vencidas,
			
			'estado': user_filt.estado_usuario,
			'AMU': True,
			'AMI': True
		}

	return context

def enviar_historial_afiliado(request, user_log, user_filt, tam, mes, start_date, end_date):

	user_log = CustomUser.objects.get(username=user_log)  # Directivo
	user_filt = CustomUser.objects.get(username=user_filt)  # Afiliado

	if tam == 'AMU' and mes == 'None' and start_date == 'None' and end_date == 'None':

		try:
			
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')

			historial = AporteAfiliado.objects.filter(
				aporte_mensual_afil=tipo_factura.id, 
				afiliado=user_filt.id
			)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fechas': False,
				'todo': False,
				'mes': False,
				# Aportes actuales
				'fact_cobradas': len(historial),
				'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
				'fecha_historial': datetime.datetime.now().date(),
			}
	
			try:
				# CONTENIDO DEL CORREO
				asunto = f'HISTORIAL DE MIS RECAUDACIONES EN ICAP'
				msj = f'''
				
				COLEGIADO USERNAME: {user_filt.username}
				COLEGIADO C.I.: {user_filt.ci}
				COLEGIADO MATRÍCULA: {user_filt.matricula}

				HISTORIAL GENERADO POR:

				RECAUDADOR USERNAME: {user_log.username}
				RECAUDADOR C.I.: {user_log.ci}
				RECAUDADOR MATRÍCULA: {user_log.matricula}
				
				FECHA DE GENERACIÓN DE ESTE HISTORIAL: {datetime.datetime.now().date()}
				'''

				template = get_template('ProyectoApp/historial.html')
				html = template.render(context)
				result = io.BytesIO()
				pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)
				
				destinatarios = [f'{user_filt.email}', f'{user_log.email}']

				msg = EmailMultiAlternatives(asunto, msj, EMAIL_HOST_USER, destinatarios)
				
				file_to_be_sent = result.getvalue()
				
				msg.attach(
					f'historial_aportes_mensuales_{user_filt.username}.pdf',
					file_to_be_sent,
					'application/pdf')

				msg.send()

				return 1  # ENVIO CORRECTAMENTE
			
			except Exception as e:
				return 0 # ENVIO FALLO

		except Exception as e:
			return 0 # ENVIO FALLO

	elif tam == 'AMI' and mes == 'None' and start_date == 'None' and end_date == 'None':
		try:
			
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')

			historial = AporteAfiliado.objects.filter(
				aporte_mensual_afil=tipo_factura.id, 
				afiliado=user_filt.id
			)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fechas': False,
				'todo': False,
				'mes': False,
				# Aportes actuales
				'fact_cobradas': len(historial),
				'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
				'fecha_historial': datetime.datetime.now().date(),
			}
	
			try:
				# CONTENIDO DEL CORREO
				asunto = f'HISTORIAL DE MIS RECAUDACIONES EN ICAP'
				msj = f'''
				
				COLEGIADO USERNAME: {user_filt.username}
				COLEGIADO C.I.: {user_filt.ci}
				COLEGIADO MATRÍCULA: {user_filt.matricula}

				HISTORIAL GENERADO POR:

				RECAUDADOR USERNAME: {user_log.username}
				RECAUDADOR C.I.: {user_log.ci}
				RECAUDADOR MATRÍCULA: {user_log.matricula}
				
				FECHA DE GENERACIÓN DE ESTE HISTORIAL: {datetime.datetime.now().date()}
				'''

				template = get_template('ProyectoApp/historial.html')
				html = template.render(context)
				result = io.BytesIO()
				pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)
				
				destinatarios = [f'{user_filt.email}', f'{user_log.email}']

				msg = EmailMultiAlternatives(asunto, msj, EMAIL_HOST_USER, destinatarios)
				
				file_to_be_sent = result.getvalue()
				
				msg.attach(
					f'historial_aportes_mensuales_{user_filt.username}.pdf',
					file_to_be_sent,
					'application/pdf')

				msg.send()

				return 1  # ENVIO CORRECTAMENTE
			
			except Exception as e:
				return 0 # ENVIO FALLO

		except Exception as e:
			return 0 # ENVIO FALLO
	
	elif tam == 'AMU' and mes != 'None' and start_date == 'None' and end_date == 'None':
		try:
			
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
			start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
			end_date = datetime.datetime.now().date()  # Fecha actual

			historial = AporteAfiliado.objects.filter(
				afiliado=user_filt.id,
				aporte_mensual_afil=tipo_factura.id, 
				fecha_pago__range=[start_date, end_date] 
			)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fechas': False,
				'todo': False,
				'mes': True,
				# Aportes actuales
				'fact_cobradas': len(historial),
				'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
				'fecha_historial': datetime.datetime.now().date(),
				'start_date': start_date,
				'end_date': end_date
			}
			
			try:
				# CONTENIDO DEL CORREO
				asunto = f'HISTORIAL DE MIS RECAUDACIONES EN ICAP'
				msj = f'''
				
				HISTORIAL DEL {start_date} AL {end_date}

				COLEGIADO USERNAME: {user_filt.username}
				COLEGIADO C.I.: {user_filt.ci}
				COLEGIADO MATRÍCULA: {user_filt.matricula}

				HISTORIAL GENERADO POR:

				RECAUDADOR USERNAME: {user_log.username}
				RECAUDADOR C.I.: {user_log.ci}
				RECAUDADOR MATRÍCULA: {user_log.matricula}
				
				FECHA DE GENERACIÓN DE ESTE HISTORIAL: {datetime.datetime.now().date()}
				'''

				template = get_template('ProyectoApp/historial.html')
				html = template.render(context)
				result = io.BytesIO()
				pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)
				
				destinatarios = [f'{user_filt.email}', f'{user_log.email}']

				msg = EmailMultiAlternatives(asunto, msj, EMAIL_HOST_USER, destinatarios)
				
				file_to_be_sent = result.getvalue()
				
				msg.attach(
					f'historial_aportes_mensuales_{user_filt.username}.pdf',
					file_to_be_sent,
					'application/pdf')

				msg.send()

				return 1  # ENVIO CORRECTAMENTE
			
			except Exception as e:
				return 0 # ENVIO FALLO

		except Exception as e:
			return 0 # ENVIO FALLO

	elif tam == 'AMI' and mes != 'None' and start_date == 'None' and end_date == 'None':
		try:
			
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
			start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
			end_date = datetime.datetime.now().date()  # Fecha actual

			historial = AporteAfiliado.objects.filter(
				afiliado=user_filt.id,
				aporte_mensual_afil=tipo_factura.id, 
				fecha_pago__range=[start_date, end_date] 
			)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fechas': False,
				'todo': False,
				'mes': True,
				# Aportes actuales
				'fact_cobradas': len(historial),
				'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
				'fecha_historial': datetime.datetime.now().date(),
				'start_date': start_date,
				'end_date': end_date
			}
			
			try:
				# CONTENIDO DEL CORREO
				asunto = f'HISTORIAL DE MIS RECAUDACIONES EN ICAP'
				msj = f'''
				
				HISTORIAL DEL {start_date} AL {end_date}

				COLEGIADO USERNAME: {user_filt.username}
				COLEGIADO C.I.: {user_filt.ci}
				COLEGIADO MATRÍCULA: {user_filt.matricula}

				HISTORIAL GENERADO POR:

				RECAUDADOR USERNAME: {user_log.username}
				RECAUDADOR C.I.: {user_log.ci}
				RECAUDADOR MATRÍCULA: {user_log.matricula}
				
				FECHA DE GENERACIÓN DE ESTE HISTORIAL: {datetime.datetime.now().date()}
				'''

				template = get_template('ProyectoApp/historial.html')
				html = template.render(context)
				result = io.BytesIO()
				pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)
				
				destinatarios = [f'{user_filt.email}', f'{user_log.email}']

				msg = EmailMultiAlternatives(asunto, msj, EMAIL_HOST_USER, destinatarios)
				
				file_to_be_sent = result.getvalue()
				
				msg.attach(
					f'historial_aportes_mensuales_{user_filt.username}.pdf',
					file_to_be_sent,
					'application/pdf')

				msg.send()

				return 1  # ENVIO CORRECTAMENTE
			
			except Exception as e:
				return 0 # ENVIO FALLO

		except Exception as e:
			return 0 # ENVIO FALLO

	elif tam == 'AMU' and mes == 'None' and start_date != 'None' and end_date != 'None':
		try:
			
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')

			historial = AporteAfiliado.objects.filter(
				afiliado=user_filt.id,
				aporte_mensual_afil=tipo_factura.id, 
				fecha_pago__range=[start_date, end_date] 
			)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fechas': True,
				'todo': False,
				'mes': False,
				# Aportes actuales
				'fact_cobradas': len(historial),
				'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
				'fecha_historial': datetime.datetime.now().date(),
				'start_date': start_date,
				'end_date': end_date
			}
			
			try:
				# CONTENIDO DEL CORREO
				asunto = f'HISTORIAL DE MIS RECAUDACIONES EN ICAP'
				msj = f'''
				
				HISTORIAL DEL {start_date} AL {end_date}

				COLEGIADO USERNAME: {user_filt.username}
				COLEGIADO C.I.: {user_filt.ci}
				COLEGIADO MATRÍCULA: {user_filt.matricula}

				HISTORIAL GENERADO POR:

				RECAUDADOR USERNAME: {user_log.username}
				RECAUDADOR C.I.: {user_log.ci}
				RECAUDADOR MATRÍCULA: {user_log.matricula}
				
				FECHA DE GENERACIÓN DE ESTE HISTORIAL: {datetime.datetime.now().date()}
				'''

				template = get_template('ProyectoApp/historial.html')
				html = template.render(context)
				result = io.BytesIO()
				pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)
				
				destinatarios = [f'{user_filt.email}', f'{user_log.email}']

				msg = EmailMultiAlternatives(asunto, msj, EMAIL_HOST_USER, destinatarios)
				
				file_to_be_sent = result.getvalue()
				
				msg.attach(
					f'historial_aportes_mensuales_{user_filt.username}.pdf',
					file_to_be_sent,
					'application/pdf')

				msg.send()

				return 1  # ENVIO CORRECTAMENTE
			
			except Exception as e:
				return 0 # ENVIO FALLO

		except Exception as e:
			return 0 # ENVIO FALLO

	else:
		try:
			
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')

			historial = AporteAfiliado.objects.filter(
				afiliado=user_filt.id,
				aporte_mensual_afil=tipo_factura.id, 
				fecha_pago__range=[start_date, end_date] 
			)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fechas': True,
				'todo': False,
				'mes': False,
				# Aportes actuales
				'fact_cobradas': len(historial),
				'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
				'fecha_historial': datetime.datetime.now().date(),
				'start_date': start_date,
				'end_date': end_date
			}
			
			try:
				# CONTENIDO DEL CORREO
				asunto = f'HISTORIAL DE MIS RECAUDACIONES EN ICAP'
				msj = f'''
				
				HISTORIAL DEL {start_date} AL {end_date}

				COLEGIADO USERNAME: {user_filt.username}
				COLEGIADO C.I.: {user_filt.ci}
				COLEGIADO MATRÍCULA: {user_filt.matricula}

				HISTORIAL GENERADO POR:

				RECAUDADOR USERNAME: {user_log.username}
				RECAUDADOR C.I.: {user_log.ci}
				RECAUDADOR MATRÍCULA: {user_log.matricula}
				
				FECHA DE GENERACIÓN DE ESTE HISTORIAL: {datetime.datetime.now().date()}
				'''

				template = get_template('ProyectoApp/historial.html')
				html = template.render(context)
				result = io.BytesIO()
				pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)
				
				destinatarios = [f'{user_filt.email}', f'{user_log.email}']

				msg = EmailMultiAlternatives(asunto, msj, EMAIL_HOST_USER, destinatarios)
				
				file_to_be_sent = result.getvalue()
				
				msg.attach(
					f'historial_aportes_mensuales_{user_filt.username}.pdf',
					file_to_be_sent,
					'application/pdf')

				msg.send()

				return 1  # ENVIO CORRECTAMENTE
			
			except Exception as e:
				return 0 # ENVIO FALLO

		except Exception as e:
			return 0 # ENVIO FALLO

def enviar_historial_recaudador(request, user_log, user_filt, tam, mes, start_date, end_date):

	user_log = CustomUser.objects.get(username=user_log)  # Directivo
	user_filt = CustomUser.objects.get(username=user_filt)  # Recaudador

	if tam == 'AMU' and mes == 'None' and start_date == 'None' and end_date == 'None':

		try:
			
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')

			historial = AporteAfiliado.objects.filter(
				aporte_mensual_afil=tipo_factura.id, 
				recaudador=user_filt.id
			)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fechas': False,
				'todo': False,
				'mes': False,
				# Aportes actuales
				'fact_cobradas': len(historial),
				'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
				'fecha_historial': datetime.datetime.now().date(),
			}
	
			try:
				# CONTENIDO DEL CORREO
				asunto = f'HISTORIAL DE MIS RECAUDACIONES EN ICAP'
				msj = f'''
				
				RECAUDADOR USERNAME: {user_filt.username}
				RECAUDADOR C.I.: {user_filt.ci}
				RECAUDADOR MATRÍCULA: {user_filt.matricula}

				HISTORIAL GENERADO POR:

				DIRECTIVO USERNAME: {user_log.username}
				DIRECTIVO C.I.: {user_log.ci}
				DIRECTIVO MATRÍCULA: {user_log.matricula}
				
				FECHA DE GENERACIÓN DE ESTE HISTORIAL: {datetime.datetime.now().date()}
				'''

				template = get_template('ProyectoApp/directivo/historial-recaudaciones.html')
				html = template.render(context)
				result = io.BytesIO()
				pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)
				
				destinatarios = [f'{user_filt.email}', f'{user_log.email}']

				msg = EmailMultiAlternatives(asunto, msj, EMAIL_HOST_USER, destinatarios)
				
				file_to_be_sent = result.getvalue()
				
				msg.attach(
					f'historial_aportes_mensuales_{user_filt.username}.pdf',
					file_to_be_sent,
					'application/pdf')

				msg.send()

				return 1  # ENVIO CORRECTAMENTE
			
			except Exception as e:
				return 0 # ENVIO FALLO

		except Exception as e:
			return 0 # ENVIO FALLO

	elif tam == 'AMI' and mes == 'None' and start_date == 'None' and end_date == 'None':
		try:
			
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')

			historial = AporteAfiliado.objects.filter(
				aporte_mensual_afil=tipo_factura.id, 
				recaudador=user_filt.id
			)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fechas': False,
				'todo': False,
				'mes': False,
				# Aportes actuales
				'fact_cobradas': len(historial),
				'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
				'fecha_historial': datetime.datetime.now().date(),
			}
	
			try:
				# CONTENIDO DEL CORREO
				asunto = f'HISTORIAL DE MIS RECAUDACIONES EN ICAP'
				msj = f'''
				
				RECAUDADOR USERNAME: {user_filt.username}
				RECAUDADOR C.I.: {user_filt.ci}
				RECAUDADOR MATRÍCULA: {user_filt.matricula}

				HISTORIAL GENERADO POR:

				DIRECTIVO USERNAME: {user_log.username}
				DIRECTIVO C.I.: {user_log.ci}
				DIRECTIVO MATRÍCULA: {user_log.matricula}
				
				FECHA DE GENERACIÓN DE ESTE HISTORIAL: {datetime.datetime.now().date()}
				'''

				template = get_template('ProyectoApp/directivo/historial-recaudaciones.html')
				html = template.render(context)
				result = io.BytesIO()
				pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)
				
				destinatarios = [f'{user_filt.email}', f'{user_log.email}']

				msg = EmailMultiAlternatives(asunto, msj, EMAIL_HOST_USER, destinatarios)
				
				file_to_be_sent = result.getvalue()
				
				msg.attach(
					f'historial_aportes_mensuales_{user_filt.username}.pdf',
					file_to_be_sent,
					'application/pdf')

				msg.send()

				return 1  # ENVIO CORRECTAMENTE
			
			except Exception as e:
				return 0 # ENVIO FALLO

		except Exception as e:
			return 0 # ENVIO FALLO
	
	elif tam == 'AMU' and mes != 'None' and start_date == 'None' and end_date == 'None':
		try:
			
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
			start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
			end_date = datetime.datetime.now().date()  # Fecha actual

			historial = AporteAfiliado.objects.filter(
				recaudador=user_filt.id,
				aporte_mensual_afil=tipo_factura.id, 
				fecha_pago__range=[start_date, end_date] 
			)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fechas': False,
				'todo': False,
				'mes': True,
				# Aportes actuales
				'fact_cobradas': len(historial),
				'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
				'fecha_historial': datetime.datetime.now().date(),
				'start_date': start_date,
				'end_date': end_date
			}
			
			try:
				# CONTENIDO DEL CORREO
				asunto = f'HISTORIAL DE MIS RECAUDACIONES EN ICAP'
				msj = f'''
				
				HISTORIAL DEL {start_date} AL {end_date}

				RECAUDADOR USERNAME: {user_filt.username}
				RECAUDADOR C.I.: {user_filt.ci}
				RECAUDADOR MATRÍCULA: {user_filt.matricula}

				HISTORIAL GENERADO POR:

				DIRECTIVO USERNAME: {user_log.username}
				DIRECTIVO C.I.: {user_log.ci}
				DIRECTIVO MATRÍCULA: {user_log.matricula}
				
				FECHA DE GENERACIÓN DE ESTE HISTORIAL: {datetime.datetime.now().date()}
				'''

				template = get_template('ProyectoApp/directivo/historial-recaudaciones.html')
				html = template.render(context)
				result = io.BytesIO()
				pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)
				
				destinatarios = [f'{user_filt.email}', f'{user_log.email}']

				msg = EmailMultiAlternatives(asunto, msj, EMAIL_HOST_USER, destinatarios)
				
				file_to_be_sent = result.getvalue()
				
				msg.attach(
					f'historial_aportes_mensuales_{user_filt.username}.pdf',
					file_to_be_sent,
					'application/pdf')

				msg.send()

				return 1  # ENVIO CORRECTAMENTE
			
			except Exception as e:
				return 0 # ENVIO FALLO

		except Exception as e:
			return 0 # ENVIO FALLO

	elif tam == 'AMI' and mes != 'None' and start_date == 'None' and end_date == 'None':
		try:
			
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
			start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
			end_date = datetime.datetime.now().date()  # Fecha actual

			historial = AporteAfiliado.objects.filter(
				recaudador=user_filt.id,
				aporte_mensual_afil=tipo_factura.id, 
				fecha_pago__range=[start_date, end_date] 
			)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fechas': False,
				'todo': False,
				'mes': True,
				# Aportes actuales
				'fact_cobradas': len(historial),
				'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
				'fecha_historial': datetime.datetime.now().date(),
				'start_date': start_date,
				'end_date': end_date
			}
			
			try:
				# CONTENIDO DEL CORREO
				asunto = f'HISTORIAL DE MIS RECAUDACIONES EN ICAP'
				msj = f'''
				
				HISTORIAL DEL {start_date} AL {end_date}

				RECAUDADOR USERNAME: {user_filt.username}
				RECAUDADOR C.I.: {user_filt.ci}
				RECAUDADOR MATRÍCULA: {user_filt.matricula}

				HISTORIAL GENERADO POR:

				DIRECTIVO USERNAME: {user_log.username}
				DIRECTIVO C.I.: {user_log.ci}
				DIRECTIVO MATRÍCULA: {user_log.matricula}
				
				FECHA DE GENERACIÓN DE ESTE HISTORIAL: {datetime.datetime.now().date()}
				'''

				template = get_template('ProyectoApp/directivo/historial-recaudaciones.html')
				html = template.render(context)
				result = io.BytesIO()
				pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)
				
				destinatarios = [f'{user_filt.email}', f'{user_log.email}']

				msg = EmailMultiAlternatives(asunto, msj, EMAIL_HOST_USER, destinatarios)
				
				file_to_be_sent = result.getvalue()
				
				msg.attach(
					f'historial_aportes_mensuales_{user_filt.username}.pdf',
					file_to_be_sent,
					'application/pdf')

				msg.send()

				return 1  # ENVIO CORRECTAMENTE
			
			except Exception as e:
				return 0 # ENVIO FALLO

		except Exception as e:
			return 0 # ENVIO FALLO

	elif tam == 'AMU' and mes == 'None' and start_date != 'None' and end_date != 'None':
		try:
			
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')

			historial = AporteAfiliado.objects.filter(
				recaudador=user_filt.id,
				aporte_mensual_afil=tipo_factura.id, 
				fecha_pago__range=[start_date, end_date] 
			)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fechas': True,
				'todo': False,
				'mes': False,
				# Aportes actuales
				'fact_cobradas': len(historial),
				'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
				'fecha_historial': datetime.datetime.now().date(),
				'start_date': start_date,
				'end_date': end_date
			}
			
			try:
				# CONTENIDO DEL CORREO
				asunto = f'HISTORIAL DE MIS RECAUDACIONES EN ICAP'
				msj = f'''
				
				HISTORIAL DEL {start_date} AL {end_date}

				RECAUDADOR USERNAME: {user_filt.username}
				RECAUDADOR C.I.: {user_filt.ci}
				RECAUDADOR MATRÍCULA: {user_filt.matricula}

				HISTORIAL GENERADO POR:

				DIRECTIVO USERNAME: {user_log.username}
				DIRECTIVO C.I.: {user_log.ci}
				DIRECTIVO MATRÍCULA: {user_log.matricula}
				
				FECHA DE GENERACIÓN DE ESTE HISTORIAL: {datetime.datetime.now().date()}
				'''

				template = get_template('ProyectoApp/directivo/historial-recaudaciones.html')
				html = template.render(context)
				result = io.BytesIO()
				pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)
				
				destinatarios = [f'{user_filt.email}', f'{user_log.email}']

				msg = EmailMultiAlternatives(asunto, msj, EMAIL_HOST_USER, destinatarios)
				
				file_to_be_sent = result.getvalue()
				
				msg.attach(
					f'historial_aportes_mensuales_{user_filt.username}.pdf',
					file_to_be_sent,
					'application/pdf')

				msg.send()

				return 1  # ENVIO CORRECTAMENTE
			
			except Exception as e:
				return 0 # ENVIO FALLO

		except Exception as e:
			return 0 # ENVIO FALLO

	else:
		try:
			
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')

			historial = AporteAfiliado.objects.filter(
				recaudador=user_filt.id,
				aporte_mensual_afil=tipo_factura.id, 
				fecha_pago__range=[start_date, end_date] 
			)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fechas': True,
				'todo': False,
				'mes': False,
				# Aportes actuales
				'fact_cobradas': len(historial),
				'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
				'fecha_historial': datetime.datetime.now().date(),
				'start_date': start_date,
				'end_date': end_date
			}
			
			try:
				# CONTENIDO DEL CORREO
				asunto = f'HISTORIAL DE MIS RECAUDACIONES EN ICAP'
				msj = f'''
				
				HISTORIAL DEL {start_date} AL {end_date}

				RECAUDADOR USERNAME: {user_filt.username}
				RECAUDADOR C.I.: {user_filt.ci}
				RECAUDADOR MATRÍCULA: {user_filt.matricula}

				HISTORIAL GENERADO POR:

				DIRECTIVO USERNAME: {user_log.username}
				DIRECTIVO C.I.: {user_log.ci}
				DIRECTIVO MATRÍCULA: {user_log.matricula}
				
				FECHA DE GENERACIÓN DE ESTE HISTORIAL: {datetime.datetime.now().date()}
				'''

				template = get_template('ProyectoApp/directivo/historial-recaudaciones.html')
				html = template.render(context)
				result = io.BytesIO()
				pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)
				
				destinatarios = [f'{user_filt.email}', f'{user_log.email}']

				msg = EmailMultiAlternatives(asunto, msj, EMAIL_HOST_USER, destinatarios)
				
				file_to_be_sent = result.getvalue()
				
				msg.attach(
					f'historial_aportes_mensuales_{user_filt.username}.pdf',
					file_to_be_sent,
					'application/pdf')

				msg.send()

				return 1  # ENVIO CORRECTAMENTE
			
			except Exception as e:
				return 0 # ENVIO FALLO

		except Exception as e:
			return 0 # ENVIO FALLO

def exportar_historial(request, user_log, user_filt, tam):
	
	if tam == 'AMU':

		try:
			user_log = CustomUser.objects.get(username=user_log)  # Directivo/Recaudador
			user_filt = CustomUser.objects.get(username=user_filt)  # Afiliado

			# FACTURAS POR APORTES MENSUALES
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
			
			# Fecha de inicio de cobros mensuales
			fecha_inicio = user_filt.fecha_registro

			fact_emitidas = int((datetime.datetime.now().date() - fecha_inicio).days / 30)	
			if fact_emitidas <= 0:
				fact_emitidas = 1
			else:
				fact_emitidas+=1


			historial = AporteAfiliado.objects.filter(
									afiliado=user_filt.id,
									aporte_mensual_afil=tipo_factura.id
									).order_by('-fecha_pago')
				
			fact_pagadas = len(historial)
			fact_vencidas = sum([fact_emitidas, -fact_pagadas])

			deuda = fact_vencidas * int(tipo_factura.aporte_mensual)
			total_aportado = fact_pagadas * int(tipo_factura.aporte_mensual)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fact_emitidas': fact_emitidas,
				'fact_pagadas': fact_pagadas,
				'fact_pendientes': sum([fact_emitidas, -fact_pagadas]),
				'deuda': deuda,
				'total_aportado': total_aportado,
				'estado': user_filt.estado_usuario,
				'monto': tipo_factura.aporte_mensual,
				'fecha_historial': datetime.datetime.now().date()
			}

			return context

		except Exception as e:
			user_log = CustomUser.objects.get(username=user_log)
			context = {'user_log': user_log}
			return context

	else:
		try:
			user_log = CustomUser.objects.get(username=user_log)  # Directivo/Recaudador
			user_filt = CustomUser.objects.get(username=user_filt)  # Afiliado

			# FACTURAS POR APORTES MENSUALES
			tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
			tipo_factura_nueva = AporteMensual.objects.get(aporte_mensual_deno='AMU')

			# Fecha de inicio de cobros mensuales
			fecha_inicio = tipo_factura.fecha_inicio_cobros
			fecha_final = tipo_factura_nueva.fecha_inicio_cobros

			fact_emitidas = int((fecha_final - fecha_inicio).days / 30)		
			
			historial = AporteAfiliado.objects.filter(
									afiliado=user_filt.id,
									aporte_mensual_afil=tipo_factura.id
									).order_by('-fecha_pago')
			
			fact_pagadas = len(historial)
			fact_vencidas = sum([fact_emitidas, -fact_pagadas])

			deuda = fact_vencidas * int(tipo_factura.aporte_mensual)
			total_aportado = fact_pagadas * int(tipo_factura.aporte_mensual)

			context = {
				'user_log': user_log,
				'user_filt': user_filt,
				'historial': historial,
				'fact_emitidas': fact_emitidas,
				'fact_pagadas': fact_pagadas,
				'fact_pendientes': sum([fact_emitidas, -fact_pagadas]),
				'deuda': deuda,
				'total_aportado': total_aportado,
				'estado': user_filt.estado_usuario,
				'monto': tipo_factura.aporte_mensual,
				'fecha_historial': datetime.datetime.now().date()
			}

			return context

		except Exception as e:
			user_log = CustomUser.objects.get(username=user_log)
			context = {'user_log': user_log}
			return context

def exportar_historial_recaud(request, user_log, user_filt, tam, mes, start_date, end_date):
	user_log = CustomUser.objects.get(username=user_log) # Directivo que genera el historial
	user_filt = CustomUser.objects.get(username=user_filt) # Recaudador
	
	if tam == 'AMU' and mes == 'None' and start_date == 'None' and end_date == 'None':
		
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')

		historial = AporteAfiliado.objects.filter(
			recaudador=user_filt.id,
			aporte_mensual_afil=tipo_factura.id, 
		).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'user_filt': user_filt,
			'historial': historial,
			'fechas': False,
			'todo': False,
			'mes': False,
			# Aportes actuales
			'fact_cobradas': len(historial),
			'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
			'fecha_historial': datetime.datetime.now().date(),
		}
		
	elif tam == 'AMI' and mes == 'None' and start_date == 'None' and end_date == 'None':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')

		historial = AporteAfiliado.objects.filter(
			recaudador=user_filt.id,
			aporte_mensual_afil=tipo_factura.id, 
		).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'user_filt': user_filt,
			'historial': historial,
			'fechas': False,
			'todo': False,
			'mes': False,
			# Aportes actuales
			'fact_cobradas': len(historial),
			'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
			'fecha_historial': datetime.datetime.now().date(),
		}
	
	elif tam == 'AMU' and mes != 'None' and start_date == 'None' and end_date == 'None':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
		start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
		end_date = datetime.datetime.now().date()  # Fecha actual

		historial = AporteAfiliado.objects.filter(
			recaudador=user_filt.id,
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date] 
		).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'user_filt': user_filt,
			'historial': historial,
			'fechas': False,
			'todo': False,
			'mes': True,
			# Aportes actuales
			'fact_cobradas': len(historial),
			'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
			'fecha_historial': datetime.datetime.now().date(),
			'start_date': start_date,
			'end_date': end_date
		}

	elif tam == 'AMI' and mes != 'None' and start_date == 'None' and end_date == 'None':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
		start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
		end_date = datetime.datetime.now().date()  # Fecha actual

		historial = AporteAfiliado.objects.filter(
			recaudador=user_filt.id,
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date] 
		).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'user_filt': user_filt,
			'historial': historial,
			'fechas': False,
			'todo': False,
			'mes': True,
			# Aportes actuales
			'fact_cobradas': len(historial),
			'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
			'fecha_historial': datetime.datetime.now().date(),
			'start_date': start_date,
			'end_date': end_date
		}

	elif tam == 'AMU' and mes == 'None' and start_date != 'None' and end_date != 'None':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
		
		historial = AporteAfiliado.objects.filter(
			recaudador=user_filt.id,
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date] 
		).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'user_filt': user_filt,
			'historial': historial,
			'fechas': True,
			'todo': False,
			'mes': False,
			# Aportes actuales
			'fact_cobradas': len(historial),
			'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
			'fecha_historial': datetime.datetime.now().date(),
			'start_date': start_date,
			'end_date': end_date
		}

	else:
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
		
		historial = AporteAfiliado.objects.filter(
			recaudador=user_filt.id,
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date] 
		).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'user_filt': user_filt,
			'historial': historial,
			'fechas': True,
			'todo': False,
			'mes': False,
			# Aportes actuales
			'fact_cobradas': len(historial),
			'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
			'fecha_historial': datetime.datetime.now().date(),
			'start_date': start_date,
			'end_date': end_date
		}

	return context

def exportar_mis_recaudaciones(request, user_log):
	user_log = CustomUser.objects.get(username=user_log)
	tipo_factura_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	tipo_factura_inicial = AporteMensual.objects.get(aporte_mensual_deno='AMI')
	
	aportes_actuales = AporteAfiliado.objects.filter(
							aporte_mensual_afil=tipo_factura_actual.id, 
							recaudador=user_log.id
							).order_by('-fecha_pago')

	aportes_iniciales = AporteAfiliado.objects.filter(
							aporte_mensual_afil=tipo_factura_inicial.id, 
							recaudador=user_log.id
							).order_by('-fecha_pago')

	context = {
		'user_log': user_log,
		'fecha_historial': datetime.datetime.now().date(),
		'todo': True,

		# Aportes actuales
		'aportes_actuales': aportes_actuales,
		'cantidad_actuales': len(aportes_actuales),
		'monto_recaudado_actual': len(aportes_actuales) * int(tipo_factura_actual.aporte_mensual),
		
		# Aportes iniciales
		'aportes_iniciales': aportes_iniciales,
		'cantidad_iniciales': len(aportes_iniciales),
		'monto_recaudado_inicial': len(aportes_iniciales) * int(tipo_factura_inicial.aporte_mensual),

		# TOTAL
		'cantidad_total': sum([len(aportes_actuales), len(aportes_iniciales)]),
		'monto_recaudado_total': len(aportes_actuales) * int(tipo_factura_actual.aporte_mensual) + len(aportes_iniciales) * int(tipo_factura_inicial.aporte_mensual)
	}

	return context

def exportar_mis_recaudaciones_mes(request, user_log):
	
	start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
	end_date = datetime.datetime.now().date()  # Fecha actual
	
	user_log = CustomUser.objects.get(username=user_log)
	tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	
	aportes = AporteAfiliado.objects.filter(
							aporte_mensual_afil=tipo_factura.id,
							recaudador=user_log.id,
							fecha_pago__range=[start_date, end_date]
							).order_by('-fecha_pago')

	context = {
		'user_log': user_log,
		'aportes': aportes,
		'cantidad': len(aportes),
		'monto_recaudado': len(aportes) * int(tipo_factura.aporte_mensual),
		'fecha_historial': datetime.datetime.now().date(),
		'mes': True,
		'start_date': start_date,
		'end_date': end_date

	}

	return context

def exportar_mis_recaudaciones_fechas(request, user_log, start_date, end_date):
	
	user_log = CustomUser.objects.get(username=user_log)
	
	tipo_factura_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	tipo_factura_inicial = AporteMensual.objects.get(aporte_mensual_deno='AMI')
	

	aportes_actuales = AporteAfiliado.objects.filter(
							aporte_mensual_afil=tipo_factura_actual.id,
							recaudador=user_log.id,
							fecha_pago__range=[start_date, end_date]
							)

	aportes_iniciales = AporteAfiliado.objects.filter(
							aporte_mensual_afil=tipo_factura_inicial.id,
							recaudador=user_log.id,
							fecha_pago__range=[start_date, end_date]
							).order_by('-fecha_pago')

	context = {
		'user_log': user_log,
		'start_date': start_date,
		'end_date': end_date,
		'todo': True,
		'fechas': True,
		'fecha_historial': datetime.datetime.now().date(),

		# Aportes actuales
		'aportes_actuales': aportes_actuales,
		'cantidad_actuales': len(aportes_actuales),
		'monto_recaudado_actual': len(aportes_actuales) * int(tipo_factura_actual.aporte_mensual),
		
		# Aportes iniciales
		'aportes_iniciales': aportes_iniciales,
		'cantidad_iniciales': len(aportes_iniciales),
		'monto_recaudado_inicial': len(aportes_iniciales) * int(tipo_factura_inicial.aporte_mensual),
		
		# TOTAL
		'cantidad_total': sum([len(aportes_actuales), len(aportes_iniciales)]),
		'monto_recaudado_total': len(aportes_actuales) * int(tipo_factura_actual.aporte_mensual) + len(aportes_iniciales) * int(tipo_factura_inicial.aporte_mensual)
		
	}

	return context

def recaud_exportar_historial_afil(request, user_log, user_filt, tam, mes, start_date, end_date):
	''' EXPORTA A PDF EL HISTORIAL DEL AFILIADO '''
	user_log = CustomUser.objects.get(username=user_log) # Directivo/Recaudador que genera el historial
	user_filt = CustomUser.objects.get(username=user_filt) # Afiliado
	
	if tam == 'AMU' and mes == 'None' and start_date == 'None' and end_date == 'None':
		
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')

		historial = AporteAfiliado.objects.filter(
			afiliado=user_filt.id,
			aporte_mensual_afil=tipo_factura.id, 
		).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'user_filt': user_filt,
			'historial': historial,
			'fechas': False,
			'todo': False,
			'mes': False,
			# Aportes actuales
			'fact_cobradas': len(historial),
			'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
			'fecha_historial': datetime.datetime.now().date(),
			'monto_unit': tipo_factura.aporte_mensual,
		}
		
	elif tam == 'AMI' and mes == 'None' and start_date == 'None' and end_date == 'None':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')

		historial = AporteAfiliado.objects.filter(
			afiliado=user_filt.id,
			aporte_mensual_afil=tipo_factura.id, 
		).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'user_filt': user_filt,
			'historial': historial,
			'fechas': False,
			'todo': False,
			'mes': False,
			# Aportes actuales
			'fact_cobradas': len(historial),
			'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
			'fecha_historial': datetime.datetime.now().date(),
			'monto_unit': tipo_factura.aporte_mensual,
		}
	
	elif tam == 'AMU' and mes != 'None' and start_date == 'None' and end_date == 'None':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
		start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
		end_date = datetime.datetime.now().date()  # Fecha actual

		historial = AporteAfiliado.objects.filter(
			afiliado=user_filt.id,
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date] 
		).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'user_filt': user_filt,
			'historial': historial,
			'fechas': False,
			'todo': False,
			'mes': True,
			# Aportes actuales
			'fact_cobradas': len(historial),
			'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
			'fecha_historial': datetime.datetime.now().date(),
			'start_date': start_date,
			'end_date': end_date,
			'monto_unit': tipo_factura.aporte_mensual,
		}

	elif tam == 'AMI' and mes != 'None' and start_date == 'None' and end_date == 'None':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
		start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
		end_date = datetime.datetime.now().date()  # Fecha actual

		historial = AporteAfiliado.objects.filter(
			afiliado=user_filt.id,
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date] 
		).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'user_filt': user_filt,
			'historial': historial,
			'fechas': False,
			'todo': False,
			'mes': True,
			# Aportes actuales
			'fact_cobradas': len(historial),
			'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
			'fecha_historial': datetime.datetime.now().date(),
			'start_date': start_date,
			'end_date': end_date,
			'monto_unit': tipo_factura.aporte_mensual,
		}

	elif tam == 'AMU' and mes == 'None' and start_date != 'None' and end_date != 'None':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
		
		historial = AporteAfiliado.objects.filter(
			afiliado=user_filt.id,
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date] 
		).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'user_filt': user_filt,
			'historial': historial,
			'fechas': True,
			'todo': False,
			'mes': False,
			# Aportes actuales
			'fact_cobradas': len(historial),
			'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
			'fecha_historial': datetime.datetime.now().date(),
			'start_date': start_date,
			'end_date': end_date,
			'monto_unit': tipo_factura.aporte_mensual,
		}

	else:
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
		
		historial = AporteAfiliado.objects.filter(
			afiliado=user_filt.id,
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date] 
		).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'user_filt': user_filt,
			'historial': historial,
			'fechas': True,
			'todo': False,
			'mes': False,
			# Aportes actuales
			'fact_cobradas': len(historial),
			'monto_recaudado': len(historial) * int(tipo_factura.aporte_mensual),
			'fecha_historial': datetime.datetime.now().date(),
			'start_date': start_date,
			'end_date': end_date,
			'monto_unit': tipo_factura.aporte_mensual,
		}

	return context

def exportar_historial_afil(request, user_log, tam, th, start_date, end_date):
	user_log = CustomUser.objects.get(username=user_log)  # AFILIADO

	if tam == 'AMU' and th == 'TODO' and start_date == 'None' and end_date == 'None':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
		
		# Fecha de inicio de cobros mensuales
		fecha_inicio = user_log.fecha_registro

		fact_emitidas = int((datetime.datetime.now().date() - fecha_inicio).days / 30)	
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1

		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id
								).order_by('-fecha_pago')
			
		fact_pagadas = len(historial)
	
		context = {
			'user_log': user_log,
			'historial': historial,
			'fact_emitidas': fact_emitidas,
			'fact_pagadas': fact_pagadas,
			'fact_pendientes': sum([fact_emitidas, -fact_pagadas]),
			'deuda': sum([fact_emitidas, -fact_pagadas]) * int(tipo_factura.aporte_mensual),
			'total_aportado': fact_pagadas * int(tipo_factura.aporte_mensual),
			'estado': user_log.estado_usuario,
			'monto_unit': tipo_factura.aporte_mensual,
			'fecha_historial': datetime.datetime.now().date()
		}

	elif tam == 'AMI' and th == 'TODO' and start_date == 'None' and end_date == 'None':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
		tipo_factura_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')

		# Fecha de inicio de cobros mensuales
		fecha_inicio = tipo_factura.fecha_inicio_cobros
		fecha_final = tipo_factura_actual.fecha_inicio_cobros

		fact_emitidas = int((fecha_final - fecha_inicio).days / 30)	
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1

		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id
								).order_by('-fecha_pago')
			
		fact_pagadas = len(historial)
	
		context = {
			'user_log': user_log,
			'historial': historial,
			'fact_emitidas': fact_emitidas,
			'fact_pagadas': fact_pagadas,
			'fact_pendientes': sum([fact_emitidas, -fact_pagadas]),
			'deuda': sum([fact_emitidas, -fact_pagadas]) * int(tipo_factura.aporte_mensual),
			'total_aportado': fact_pagadas * int(tipo_factura.aporte_mensual),
			'estado': user_log.estado_usuario,
			'monto_unit': tipo_factura.aporte_mensual,
			'fecha_historial': datetime.datetime.now().date()
		}

	elif tam == 'AMU' and th == 'MES' and start_date == 'None' and end_date == 'None':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
		
		start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
		end_date = datetime.datetime.now().date()  # Fecha actual
		
		# Fecha de inicio de cobros mensuales
		fecha_inicio = user_log.fecha_registro

		fact_emitidas = int((datetime.datetime.now().date() - fecha_inicio).days / 30)	
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1

		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id,
								).order_by('-fecha_pago')
			
		fact_pagadas = len(historial)
		
		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id,
								fecha_pago__range=[start_date, end_date]
								).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'historial': historial,
			'fact_emitidas': fact_emitidas,
			'fact_pagadas': fact_pagadas,
			'fact_pendientes': sum([fact_emitidas, -fact_pagadas]),
			'deuda': sum([fact_emitidas, -fact_pagadas]) * int(tipo_factura.aporte_mensual),
			'total_aportado': fact_pagadas * int(tipo_factura.aporte_mensual),
			'estado': user_log.estado_usuario,
			'monto_unit': tipo_factura.aporte_mensual,
			'fecha_historial': datetime.datetime.now().date(),
			'start_date': start_date,
			'end_date': end_date
		}

	elif tam == 'AMI' and th == 'MES' and start_date == 'None' and end_date == 'None':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
		tipo_factura_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')

		# Fecha de inicio de cobros mensuales
		fecha_inicio = tipo_factura.fecha_inicio_cobros
		fecha_final = tipo_factura_actual.fecha_inicio_cobros

		fact_emitidas = int((fecha_final - fecha_inicio).days / 30)	
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1

		start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
		end_date = datetime.datetime.now().date()  # Fecha actual
		
		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id,
								).order_by('-fecha_pago')

		fact_pagadas = len(historial)

		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id,
								fecha_pago__range=[start_date, end_date]
								).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'historial': historial,
			'fact_emitidas': fact_emitidas,
			'fact_pagadas': fact_pagadas,
			'fact_pendientes': sum([fact_emitidas, -fact_pagadas]),
			'deuda': sum([fact_emitidas, -fact_pagadas]) * int(tipo_factura.aporte_mensual),
			'total_aportado': len(historial) * int(tipo_factura.aporte_mensual),
			'estado': user_log.estado_usuario,
			'monto_unit': tipo_factura.aporte_mensual,
			'fecha_historial': datetime.datetime.now().date(),
			'start_date': start_date,
			'end_date': end_date
		}


	elif tam == 'AMU' and th == 'None' and start_date != 'None' and end_date != 'None':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
		
		# Fecha de inicio de cobros mensuales
		fecha_inicio = user_log.fecha_registro

		fact_emitidas = int((datetime.datetime.now().date() - fecha_inicio).days / 30)	
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1

		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id,
								).order_by('-fecha_pago')
			
		fact_pagadas = len(historial)
		
		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id,
								fecha_pago__range=[start_date, end_date]
								).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'historial': historial,
			'fact_emitidas': fact_emitidas,
			'fact_pagadas': fact_pagadas,
			'fact_pendientes': sum([fact_emitidas, -fact_pagadas]),
			'deuda': sum([fact_emitidas, -fact_pagadas]) * int(tipo_factura.aporte_mensual),
			'total_aportado': fact_pagadas * int(tipo_factura.aporte_mensual),
			'estado': user_log.estado_usuario,
			'monto_unit': tipo_factura.aporte_mensual,
			'fecha_historial': datetime.datetime.now().date(),
			'start_date': start_date,
			'end_date': end_date
		}

	else:
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
		tipo_factura_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')

		# Fecha de inicio de cobros mensuales
		fecha_inicio = tipo_factura.fecha_inicio_cobros
		fecha_final = tipo_factura_actual.fecha_inicio_cobros

		fact_emitidas = int((fecha_final - fecha_inicio).days / 30)	
		if fact_emitidas <= 0:
			fact_emitidas = 1
		else:
			fact_emitidas+=1

		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id,
								).order_by('-fecha_pago')

		fact_pagadas = len(historial)

		historial = AporteAfiliado.objects.filter(
								afiliado=user_log.id,
								aporte_mensual_afil=tipo_factura.id,
								fecha_pago__range=[start_date, end_date]
								).order_by('-fecha_pago')

		context = {
			'user_log': user_log,
			'historial': historial,
			'fact_emitidas': fact_emitidas,
			'fact_pagadas': fact_pagadas,
			'fact_pendientes': sum([fact_emitidas, -fact_pagadas]),
			'deuda': sum([fact_emitidas, -fact_pagadas]) * int(tipo_factura.aporte_mensual),
			'total_aportado': len(historial) * int(tipo_factura.aporte_mensual),
			'estado': user_log.estado_usuario,
			'monto_unit': tipo_factura.aporte_mensual,
			'fecha_historial': datetime.datetime.now().date(),
			'start_date': start_date,
			'end_date': end_date
		}
	
	return context	

def historial_afiliado(request, user_log, afiliado, tam, th):
	user_log = CustomUser.objects.get(username=user_log)
	afiliado = CustomUser.objects.get(username=afiliado)

	if tam == 'AMU':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
		
	else:
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
	
	try:
		
		historial = AporteAfiliado.objects.filter(
								afiliado=afiliado.id,
								aporte_mensual_afil=tipo_factura.id
								).order_by('-fecha_pago')

		cant_aportes = len(historial)
		monto = len(historial) * int(tipo_factura.aporte_mensual)

		paginator = Paginator(historial, 10)  # Mostrará hasta 10 historial por pág.
		page = request.GET.get('page')
		historial = paginator.get_page(page)

		context = {
			'user_log': user_log,
			'tam': tam,
			'afiliado': afiliado,
			'historial': historial,
			'cant_aportes': cant_aportes,
			'monto': monto
			}

		return context

	except:
		
		context = {
			'user_log': user_log
			}

		return context

def historial_recaud_mes(request, user_log, recaudador, tam, th):
	user_log = CustomUser.objects.get(username=user_log)
	recaudador = CustomUser.objects.get(username=recaudador)
	tipo_factura = AporteMensual.objects.get(aporte_mensual_deno=tam)

	start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
	end_date = datetime.datetime.now().date()  # Fecha actual
		
	try:
		historial = AporteAfiliado.objects.filter(
			recaudador=recaudador.id,
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date]
			).order_by('-fecha_pago')
	except:
		historial = None

	# Configuración para el espacio de paginación
	paginator = Paginator(historial, 15)  # Mostrará hasta 15 historial por pág.
	page = request.GET.get('page')
	historial = paginator.get_page(page)
	
	context = {
		'user_log': user_log,
		'recaudador': recaudador,
		'historial': historial,
		'cant_cobros': len(historial),
		'monto': tipo_factura.aporte_mensual,
		'tam': tam,
		'monto_unit': tipo_factura.aporte_mensual,
		'th': th
	}

	return context

def historial_recaud(request, user_log, recaudador, tam, th):

	user_log = CustomUser.objects.get(username=user_log)
	recaudador = CustomUser.objects.get(username=recaudador)

	if tam == 'AMU':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	else:
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
	
	try:
		
		historial = AporteAfiliado.objects.filter(
								recaudador=recaudador.id,
								aporte_mensual_afil=tipo_factura.id
								).order_by('-fecha_pago')

		cant_cobros = len(historial)
		monto = len(historial) * int(tipo_factura.aporte_mensual)

		paginator = Paginator(historial, 15)  # Mostrará hasta 15 historial por pág.
		page = request.GET.get('page')
		historial = paginator.get_page(page)

		context = {
			'user_log': user_log,
			'tam': tam,
			'recaudador': recaudador,
			'historial': historial,
			'cant_cobros': cant_cobros,
			'monto': monto,
			'monto_unit': tipo_factura.aporte_mensual,
			'th': th  # Tipo de historial (TOTAL, MES, FECHAS)
			}

		return context

	except:
		
		context = {
			'user_log': user_log
			}

		return context

def historial_recaud_fechas(request, user_log, recaudador, tam, th, start_date, end_date):
	user_log = CustomUser.objects.get(username=user_log)
	user_filt = CustomUser.objects.get(username=recaudador)
	
	if tam == 'AMU':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	else:
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')

	try:
		historial = AporteAfiliado.objects.filter(
			recaudador=user_filt.id,
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date]
			).order_by('-fecha_pago')
	except:
		historial = None

	cant_cobros = len(historial)
	monto = len(historial) * int(tipo_factura.aporte_mensual)

	# Configuración para el espacio de paginación
	paginator = Paginator(historial, 15)  # Mostrará hasta 15 historial por pág.
	page = request.GET.get('page')
	historial = paginator.get_page(page)
	
	context = {
		'user_log': user_log,
		'recaudador': user_filt,
		'historial': historial,
		'tam': tam,
		'th': th,
		'cant_cobros': cant_cobros,
		'monto': monto,
		'monto_unit': tipo_factura.aporte_mensual,
		'start_date': start_date,
		'end_date': end_date
	}

	return context

def historial_recaud_simple(recaudador, tam):

	recaudador = CustomUser.objects.get(username=recaudador)

	if tam == 'AMU':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	else:
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
	
	historial = AporteAfiliado.objects.filter(
							recaudador=recaudador.id,
							aporte_mensual_afil=tipo_factura.id
							).order_by('-fecha_pago')

	cant_cobros = len(historial)
	monto = len(historial) * int(tipo_factura.aporte_mensual)

	try:
		ult_aporte = historial[0].fecha_pago

	except:
		ult_aporte = 'SIN REGISTRO'

	context = {
		'ult_aporte': ult_aporte,
		'cant_cobros': cant_cobros,
		'monto': monto
		
		}

	return context

def contar_recaudadores():

	return len(CustomUser.objects.filter(groups__name='Recaudador'))

def contar_afiliados():

	return len(CustomUser.objects.filter(groups__name='Afiliado'))

def contar_directivos():

	return len(CustomUser.objects.filter(groups__name='Directivo'))

def info_deuda_general():
	''' CONTAR DEUDA POR APORTES MENSUALES '''
	
	afiliados = CustomUser.objects.filter(groups__name='Afiliado')

	deudas_afiliados = []

	for afiliado in afiliados:
		context = cal_deuda_afiliado_simple(afiliado.username)
		deudas_afiliados.append(context['deuda'])
		deudas_afiliados.append(context['deuda_ami'])
	
	deuda_total = 0
	for deuda_afil in deudas_afiliados:
		if deuda_afil > 0:
			deuda_total += deuda_afil

	return deuda_total

def monto_recaudar_mes():
	tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	
	try:
		return (contar_afiliados() * int(tipo_factura.aporte_mensual))

	except Exception as e:
		return 0

def monto_recaudado_mes():
	
	tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	
	start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
	end_date = datetime.datetime.now().date()  # Fecha actual

	try:
		aportes = AporteAfiliado.objects.filter(
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date]
			)
		
		a = 0
		for a in range(0, len(aportes)):
			a += 1  # Cuenta cuántos aportes se realizaron desde el rango de tiempo mensual
			
		return (int(a) * int(tipo_factura.aporte_mensual))

	except Exception as e:
		return 0 

def aportes_cert_mes():
	tipo_factura = AporteCertificacion.objects.get(aporte_certificacion_deno='CERTIFICADO')
	
	start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
	end_date = datetime.datetime.now().date()  # Fecha actual

	try:
		aportes = AporteAfiliado.objects.filter(
			aporte_certif_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date]
			)
		
		a = 0
		for a in range(0, len(aportes)):
			a += 1  # Cuenta cuántos aportes se realizaron desde el rango de tiempo mensual
			
		return (int(a) * int(tipo_factura.aporte_certificacion))

	except Exception as e:
		return 0

def aportes_dona_mes():
	start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
	end_date = datetime.datetime.now().date()  # Fecha actual



	am_amu = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	am_ami = AporteMensual.objects.get(aporte_mensual_deno='AMI')
	aporte_cert = AporteCertificacion.objects.get(aporte_certificacion_deno='CERTIFICADO')
	
	try:
		aportes = AporteAfiliado.objects.filter(
			fecha_pago__range=[start_date, end_date]
			).exclude(
				aporte_mensual_afil__id__in=[am_amu.id, am_ami.id],
				aporte_certif_afil__id__in=[aporte_cert.id],
				)
		i = 0
		for a in aportes:
			i += int(a.aporte_dona_afil)

		return i

	except Exception as e:
		#print(e)
		return 0

def nuevos_afiliados_mes():

	try:
		start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
		end_date = datetime.datetime.now().date()  # Fecha actual
		
		afiliados_nuevos = CustomUser.objects.filter(
							groups__name='Afiliado',
							fecha_registro__range=[start_date, end_date]
							)

		return len(afiliados_nuevos)

	except:
		return 0

def generar_info_direc(request, user_log):
	
	user_log = CustomUser.objects.get(username=user_log)

	try:
		recaudadores = CustomUser.objects.filter(groups__name='Recaudador').order_by('-fecha_registro')
	except:
		recaudadores = None

	# Configuración para el espacio de paginación
	paginator = Paginator(recaudadores, 30)  # Mostrará hasta 30 recaudadores por pág.
	page = request.GET.get('page')
	recaudadores = paginator.get_page(page)
	
	context = {
		'user_log': user_log,
		'recaudadores': recaudadores,
	}

	return context

def historial_afil(request, user_log, user_filt, tam, th):

	user_log = CustomUser.objects.get(username=user_log)
	afiliado = CustomUser.objects.get(username=user_filt)

	if tam == 'AMU':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	else:
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')
	
	historial = AporteAfiliado.objects.filter(
							afiliado=afiliado.id,
							aporte_mensual_afil=tipo_factura.id
							).order_by('-fecha_pago')

	cant_aportes = len(historial)
	monto = len(historial) * int(tipo_factura.aporte_mensual)

	paginator = Paginator(historial, 15)  # Mostrará hasta 15 historial por pág.
	page = request.GET.get('page')
	historial = paginator.get_page(page)

	context = {
		'user_log': user_log,
		'tam': tam,
		'afiliado': afiliado,
		'historial': historial,
		'cant_aportes': cant_aportes,
		'monto': monto,
		'monto_unit': tipo_factura.aporte_mensual,
		'th': th  # Tipo de historial (TOTAL, MES, FECHAS)
		}

	return context

def historial_afil_mes(request, user_log, afiliado, tam, th):
	user_log = CustomUser.objects.get(username=user_log)
	afiliado = CustomUser.objects.get(username=afiliado)
	tipo_factura = AporteMensual.objects.get(aporte_mensual_deno=tam)

	start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
	end_date = datetime.datetime.now().date()  # Fecha actual
		
	try:
		historial = AporteAfiliado.objects.filter(
			afiliado=afiliado.id,
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date]
			).order_by('-fecha_pago')
	except:
		historial = None

	# Configuración para el espacio de paginación
	paginator = Paginator(historial, 15)  # Mostrará hasta 15 historial por pág.
	page = request.GET.get('page')
	historial = paginator.get_page(page)
	
	context = {
		'user_log': user_log,
		'afiliado': afiliado,
		'historial': historial,
		'cant_aportes': len(historial),
		'monto': len(historial) * int(tipo_factura.aporte_mensual),
		'tam': tam,
		'monto_unit': tipo_factura.aporte_mensual,
		'th': th
	}

	return context

def historial_afil_fechas(request, user_log, afiliado, tam, th, start_date, end_date):
	user_log = CustomUser.objects.get(username=user_log)
	user_filt = CustomUser.objects.get(username=afiliado)
	
	if tam == 'AMU':
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	else:
		tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMI')

	try:
		historial = AporteAfiliado.objects.filter(
			afiliado=user_filt.id,
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date]
			).order_by('-fecha_pago')
	except:
		historial = None

	cant_cobros = len(historial)
	monto = len(historial) * int(tipo_factura.aporte_mensual)

	# Configuración para el espacio de paginación
	paginator = Paginator(historial, 15)  # Mostrará hasta 15 historial por pág.
	page = request.GET.get('page')
	historial = paginator.get_page(page)
	
	context = {
		'user_log': user_log,
		'afiliado': user_filt,
		'historial': historial,
		'tam': tam,
		'th': th,
		'cant_aportes': cant_cobros,
		'monto': monto,
		'monto_unit': tipo_factura.aporte_mensual,
		'start_date': start_date,
		'end_date': end_date
	}

	return context

def generar_info_direc_afiliados(request, user_log):

	user_log = CustomUser.objects.get(username=user_log)

	try:
		afiliados = CustomUser.objects.filter(groups__name='Afiliado').order_by('-fecha_registro')
	except:
		afiliados = None

	# Configuración para el espacio de paginación
	paginator = Paginator(afiliados, 30)  # Mostrará hasta 5 afiliados por pág.
	page = request.GET.get('page')
	afiliados = paginator.get_page(page)
	
	context = {
		'user_log': user_log,
		'afiliados': afiliados
	}

	return context

def generar_info_direc_afiliados_desh(request, user_log):
	user_log = CustomUser.objects.get(username=user_log)

	try:
		afiliados = CustomUser.objects.filter(
					groups__name='Afiliado',
					estado_usuario=False
					).order_by('-fecha_registro')
	except:
		afiliados = None

	# Configuración para el espacio de paginación
	paginator = Paginator(afiliados, 30)  # Mostrará hasta 30 afiliados por pág.
	page = request.GET.get('page')
	afiliados = paginator.get_page(page)
	
	context = {
		'user_log': user_log,
		'afiliados': afiliados
	}

	return context

def cal_deuda_afiliado_reporte(user_filt):

	try:
		user_filt = CustomUser.objects.get(username=user_filt)  # Afiliado

		context_deuda = cal_deuda_afiliado_simple(user_filt.username)
		
		deuda = sum([context_deuda['deuda_ami'], context_deuda['deuda']])

		if deuda > 0:

			context = {
				'user_filt': user_filt,

				'fact_emitidas': sum([context_deuda['fact_emitidas_ami'], context_deuda['fact_emitidas']]),

				'fact_pagadas': sum([context_deuda['fact_pagadas_ami'], context_deuda['fact_pagadas']]),
				'total_aportado': sum([context_deuda['total_aportado_ami'], context_deuda['total_aportado']]),
					
				'fact_vencidas': sum([context_deuda['fact_vencidas_ami'], context_deuda['fact_vencidas']]),
				'deuda': deuda,
			}

			return context

		else:
			return None

	except Exception as e:
		return None
 
def generar_info_direc_afiliados_deudas(request, user_log):
	user_log = CustomUser.objects.get(username=user_log) # Recaudador que realiza la consulta
	tipo_factura = AporteMensual.objects.get(aporte_mensual_deno='AMU') 

	# Listar todos los afiliados:
	afiliados = CustomUser.objects.filter(groups__name='Afiliado')

	context = []
	
	for afiliado in afiliados:
		context.append(cal_deuda_afiliado_reporte(afiliado.username))
	
	while None in context:
		context.remove(None)

	return context

def generar_info_recaud_afiliados_desh(request, user_log):
	user_log = CustomUser.objects.get(username=user_log)

	try:
		afiliados = CustomUser.objects.filter(
					groups__name='Afiliado',
					estado_usuario=False
					).order_by('-fecha_registro')
	except:
		afiliados = None

	# Configuración para el espacio de paginación
	paginator = Paginator(afiliados, 30)  # Mostrará hasta 30 afiliados por pág.
	page = request.GET.get('page')
	afiliados = paginator.get_page(page)
	
	context = {
		'user_log': user_log,
		'afiliados': afiliados
	}

	return context

def filtrar_info(request, user_log, user_filt):

	user_log = CustomUser.objects.get(username=user_log)
	usuario = CustomUser.objects.get(username=user_filt)

	context = {
		'user_log': user_log,
		'usuario': usuario
	}

	return context

def directivo_ver_usuario(request, user_log, usuario):

	user_log = CustomUser.objects.get(username=user_log)
	usuario = CustomUser.objects.get(username=usuario)

	tipo_aporte = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	tipo_aporte_inicial = AporteMensual.objects.get(aporte_mensual_deno='AMI')

	if CustomUser.objects.filter(username=usuario, groups__name='Recaudador').exists():
		tipo_usuario = 'Recaudador'
		etiq_opera = 'Total de recaudaciones'
		cobros = historial_recaud_simple(usuario.username, 'AMU')

		recaudador = CustomUser.objects.get(username=user_log)

		context = {
			'user_log': user_log,
			'usuario': usuario,
			'tipo_usuario': tipo_usuario,
			'etiq_opera': etiq_opera,
			'ult_aporte': cobros['ult_aporte'],
			'fact_cobradas': cobros['cant_cobros'],
			'total_aportado': cobros['monto'],
			'monto_actual': tipo_aporte.aporte_mensual,
			'monto_inicial': tipo_aporte_inicial.aporte_mensual
		}
	
	else:
		# Es un afiliado

		tipo_aporte = AporteMensual.objects.get(aporte_mensual_deno='AMU')
		tipo_aporte_inicial = AporteMensual.objects.get(aporte_mensual_deno='AMI')

		deuda = cal_deuda_afiliado_simple(usuario.username)
		
		historial = AporteAfiliado.objects.filter(afiliado=usuario.id,
										aporte_mensual_afil=tipo_aporte_inicial.id
								).order_by('-fecha_pago')

		try:
			ult_aporte_inicial = historial[0].fecha_pago
		except:
			ult_aporte_inicial = 'SIN REGISTRO'

		historial = AporteAfiliado.objects.filter(afiliado=usuario.id,
										aporte_mensual_afil=tipo_aporte.id
								).order_by('-fecha_pago')

		try:
			ult_aporte = historial[0].fecha_pago
		except:
			ult_aporte = 'SIN REGISTRO'

		context = {
			'user_log': user_log,
			'usuario': usuario,
			'tipo_usuario': 'Afiliado',
			'etiq_opera': 'Deuda',
			'ult_aporte_inicial': ult_aporte_inicial,
			'ult_aporte': ult_aporte,
			
			'deuda_ami': deuda['deuda_ami'],
			'fact_vencidas_ami': deuda['fact_vencidas_ami'],
			'total_aportado_ami': deuda['total_aportado_ami'],

			'deuda': deuda['deuda'],
			'fact_vencidas': deuda['fact_vencidas'],
			'total_aportado': deuda['total_aportado'],
			
			'monto_actual': tipo_aporte.aporte_mensual,
			'monto_inicial': tipo_aporte_inicial.aporte_mensual,
			'AMU': deuda['AMU'],
			'AMI': deuda['AMI'],
		}

	return context

def generar_info_recaud(request, user_log):
	
	user_log = CustomUser.objects.get(username=user_log)

	try:
		afiliados = CustomUser.objects.filter(groups__name='Afiliado').order_by('-fecha_registro')
	except:
		afiliados = None

	# Configuración para el espacio de paginación
	paginator = Paginator(afiliados, 30)  # Mostrará hasta 30 afiliados por pág.
	page = request.GET.get('page')
	afiliados = paginator.get_page(page)
	
	context = {
		'user_log': user_log,
		'afiliados': afiliados
	}

	return context

def ver_kardex(request, user_log, user_filt):

	user_log = CustomUser.objects.get(username=user_log)

	if CustomUser.objects.filter(username=user_filt, groups__name='Afiliado').exists():
		tipo_usuario = 'Afiliado'

	elif CustomUser.objects.filter(username=user_filt, groups__name='Recaudador').exists():
		tipo_usuario = 'Recaudador'

	user_filt = CustomUser.objects.get(username=user_filt)

	context = {
		'user_log': user_log,
		'user_filt': user_filt,
		'tipo_usuario': tipo_usuario,
	}	

	return context

def recaudador_ver_usuario(request, user_log, usuario):

	user_log = CustomUser.objects.get(username=user_log)
	usuario = CustomUser.objects.get(username=usuario)

	tipo_aporte = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	tipo_aporte_inicial = AporteMensual.objects.get(aporte_mensual_deno='AMI')

	deuda = cal_deuda_afiliado_simple(usuario.username)
	
	historial = AporteAfiliado.objects.filter(afiliado=usuario.id,
									aporte_mensual_afil=tipo_aporte_inicial.id
							).order_by('-fecha_pago')

	try:
		ult_aporte_inicial = historial[0].fecha_pago
	except:
		ult_aporte_inicial = 'SIN REGISTRO'

	historial = AporteAfiliado.objects.filter(afiliado=usuario.id,
									aporte_mensual_afil=tipo_aporte.id
							).order_by('-fecha_pago')

	try:
		ult_aporte = historial[0].fecha_pago
	except:
		ult_aporte = 'SIN REGISTRO'

	context = {
		'user_log': user_log,
		'usuario': usuario,
		'tipo_usuario': 'Afiliado',
		'etiq_opera': 'Deuda',
		'ult_aporte_inicial': ult_aporte_inicial,
		'ult_aporte': ult_aporte,
		
		'deuda_ami': deuda['deuda_ami'],
		'fact_vencidas_ami': deuda['fact_vencidas_ami'],
		'total_aportado_ami': deuda['total_aportado_ami'],

		'deuda': deuda['deuda'],
		'fact_vencidas': deuda['fact_vencidas'],
		'total_aportado': deuda['total_aportado'],
		
		'monto_actual': tipo_aporte.aporte_mensual,
		'monto_inicial': tipo_aporte_inicial.aporte_mensual,
		'AMU': deuda['AMU'],
		'AMI': deuda['AMI'],
	}

	return context

def cal_mis_cobros(request, user_log):
	user_log = CustomUser.objects.get(username=user_log)

	try:
		cobros = AporteAfiliado.objects.filter(recaudador=user_log.id).order_by('-fecha_pago')
	except:
		cobros = None

	# Configuración para el espacio de paginación
	paginator = Paginator(cobros, 15)  # Mostrará hasta 15 cobros por pág.
	page = request.GET.get('page')
	cobros = paginator.get_page(page)
	
	context = {
		'user_log': user_log,
		'cobros': cobros
	}

	return context

def cal_mis_cobros_mes(request, user_log):
	user_log = CustomUser.objects.get(username=user_log)

	start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
	end_date = datetime.datetime.now().date()  # Fecha actual
		
	try:
		cobros = AporteAfiliado.objects.filter(
			recaudador=user_log.id,
			fecha_pago__range=[start_date, end_date]
			).order_by('-fecha_pago')
	except:
		cobros = None

	# Configuración para el espacio de paginación
	paginator = Paginator(cobros, 15)  # Mostrará hasta 15 cobros por pág.
	page = request.GET.get('page')
	cobros = paginator.get_page(page)
	
	context = {
		'user_log': user_log,
		'cobros': cobros
	}

	return context

def cal_mis_cobros_fechas(request, user_log, start_date, end_date):
	user_log = CustomUser.objects.get(username=user_log)
		
	try:
		cobros = AporteAfiliado.objects.filter(
			recaudador=user_log.id,
			fecha_pago__range=[start_date, end_date]
			).order_by('-fecha_pago')
	except:
		cobros = None

	# Configuración para el espacio de paginación
	paginator = Paginator(cobros, 15)  # Mostrará hasta 15 cobros por pág.
	page = request.GET.get('page')
	cobros = paginator.get_page(page)
	
	context = {
		'user_log': user_log,
		'cobros': cobros,
		'fechas': True,
		'start_date': start_date,
		'end_date': end_date
	}

	return context

def generar_comprobante():
	''' Función para generar comprobantes correlativos '''
	aportes = AporteAfiliado.objects.all().order_by('-comprobante')
	
	try:
		comprobante = str(sum([int(aportes[0].comprobante), 1])).zfill(6)
	except:
		comprobante = str(sum([int(00000), 1])).zfill(6)

	return comprobante

def cobrar_aporte(request, user_log, usuario, ta, form):

	user_log = CustomUser.objects.get(username=user_log)
	afiliado = CustomUser.objects.get(username=usuario)  # Afiliado al que se le registrará el aporte
	comprobante = generar_comprobante()  # Comprobante de cobro de 6 dígitos

	if ta == 1:
		# Es un aporte mensual
		aporte_mensual = AporteMensual.objects.get(
							aporte_mensual_deno=form.cleaned_data['aporte_mensual_deno']
							)
		aporte_certif_afil = None
		aporte_dona_afil = 0
		

	elif ta == 2:
		# Es un aporte por certificación
		aporte_mensual = None
		aporte_certif_afil = AporteCertificacion.objects.get(aporte_certificacion_deno='CERTIFICADO')
		aporte_dona_afil = 0

	elif ta == 3:
		# Es un aporte por donación
		aporte_mensual = None
		aporte_certif_afil = None
		aporte_dona_afil = form.cleaned_data['aporte_dona_afil']
		
	cobro = AporteAfiliado.objects.create(
					afiliado_id = afiliado.id,
					recaudador_id = user_log.id,
					aporte_mensual_afil = aporte_mensual,
					aporte_certif_afil = aporte_certif_afil,
					aporte_dona_afil = aporte_dona_afil,	
					fecha_pago = form.cleaned_data['fecha_pago'],
					comprobante = comprobante,
					talonario = form.cleaned_data['talonario']	
					)
	cobro.save()

	context = {
		'user_log': user_log,
		'comprobante': comprobante
	}
		
	return context

def cobrar_aporte_confirmado(request, user_log, usuario, ta, talon, fecha_pago, etiq,numero_recibo):
	user_log = CustomUser.objects.get(username=user_log)
	afiliado = CustomUser.objects.get(username=usuario)  # Afiliado al que se le registrará el aporte
	comprobante = generar_comprobante()  # Comprobante de cobro de 6 dígitos

	if ta == 1:
		# Es un aporte mensual
		aporte_mensual = AporteMensual.objects.get(
							aporte_mensual_deno=f'{etiq}'
							)
		aporte_certif_afil = None
		aporte_dona_afil = 0
		
	elif ta == 2:
		# Es un aporte por certificación
		aporte_mensual = None
		aporte_certif_afil = AporteCertificacion.objects.get(aporte_certificacion_deno='CERTIFICADO')
		aporte_dona_afil = 0

	elif ta == 3:
		# Es un aporte por donación
		aporte_mensual = None
		aporte_certif_afil = None
		aporte_dona_afil = etiq
	
	#Aca es donde tengo que validar la fecha para cobrarrrrr

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
		val = fecha.id

	else:
		#Aca debe de ir cuando el afiliado ya tenga facturas pagadas que debe de hacerse
		fecha = Fechas.objects.filter(agno=querie.fecha_registro.year,mes = querie.fecha_registro.month).first()
		#Ultima fecha pagada 
		val = fecha.id + len(facturas_emitidas_afiliado) 
	cobro = AporteAfiliado.objects.create(
					afiliado_id = afiliado.id,
					recaudador_id = user_log.id,
					aporte_mensual_afil = aporte_mensual,
					aporte_certif_afil = aporte_certif_afil,
					aporte_dona_afil = aporte_dona_afil,	
					fecha_pago = fecha_pago,
					comprobante = comprobante,
					talonario = talon,
					fecha_id_pago_id = val,
					numero_recibo = numero_recibo
					)
	cobro.save()
	
	context = {
		'user_log': user_log,
		'comprobante': comprobante
	}

	return context

def cobrar_aporte_mult(request, user_log, usuario, fecha_pago, cant, tam, talon,numero_recibo , fechas_pagar=None ):

	user_log = CustomUser.objects.get(username=user_log)
	usuario = CustomUser.objects.get(username=usuario)
	aporte_mensual = AporteMensual.objects.get(aporte_mensual_deno=tam)
	if fechas_pagar is None:
		for c in range(0, cant):
			comprobante = generar_comprobante()
			cobro = AporteAfiliado.objects.create(
						afiliado_id = usuario.id,
						recaudador_id = user_log.id,
						aporte_mensual_afil = aporte_mensual,
						aporte_certif_afil = None,
						aporte_dona_afil = 0,	
						fecha_pago = fecha_pago,
						comprobante = comprobante,
						talonario = talon,
					
						)
			
			cobro.save()

		context = {
			'user_log': user_log,
			'comprobante': comprobante
		}
	else:
		for c in fechas_pagar:

			comprobante = generar_comprobante()
			cobro = AporteAfiliado.objects.create(
						afiliado_id = usuario.id,
						recaudador_id = user_log.id,
						aporte_mensual_afil = aporte_mensual,
						aporte_certif_afil = None,
						aporte_dona_afil = 0,	
						fecha_pago = fecha_pago,
						comprobante = comprobante,
						talonario = talon,
						fecha_id_pago_id = c.id,
						numero_recibo = numero_recibo
						)
			cobro.save()

		context = {
			'user_log': user_log,
			'comprobante': comprobante
		}

	return context


def info_recaud(request, user_log):

	user_log = CustomUser.objects.get(username=user_log)

	context = {
		'user_log': user_log,
		'cant_recaud': contar_recaudadores(),
		'cant_afil': contar_afiliados(),
		'deuda': info_deuda_general(),
		'monto_recaudar_mes': monto_recaudar_mes(),
		'monto_recaudado_mes': monto_recaudado_mes(),
		'monto_faltante_mes': sum([monto_recaudar_mes(), -monto_recaudado_mes()]),
		'aportes_cert_mes': aportes_cert_mes(),
		'aportes_dona_mes': aportes_dona_mes(),
		'nuevos_afiliados_mes': nuevos_afiliados_mes()
	}

	return context

def info_direct(request, user_log):

	user_log = CustomUser.objects.get(username=user_log)

	context = {
		'user_log': user_log,
		'cant_recaud': contar_recaudadores(),
		'cant_afil': contar_afiliados(),
		'cant_direct': contar_directivos(),
		'deuda': info_deuda_general(),
		'monto_recaudar_mes': monto_recaudar_mes(),
		'monto_recaudado_mes': monto_recaudado_mes(),
		'monto_faltante_mes': sum([monto_recaudar_mes(), -monto_recaudado_mes()]),
		'aportes_cert_mes': aportes_cert_mes(),
		'aportes_dona_mes': aportes_dona_mes(),
		'nuevos_afiliados_mes': nuevos_afiliados_mes()
	}

	return context

def info_afil(request, user_log):
	user_log = CustomUser.objects.get(username=user_log)

	try:
		start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
		end_date = datetime.datetime.now().date()  # Fecha actual
		
		tipo_aporte = AporteMensual.objects.get(aporte_mensual_deno='AMU')

		aportes_mes = AporteAfiliado.objects.filter(
							afiliado=user_log.id,
							aporte_mensual_afil=tipo_aporte.id,
							
							)

		context = {
			'user_log': user_log
		}

		return context 

	except:
		context = {
			'user_log': user_log
		}

		return context
	

def generar_info_afil(request, user_log):
	
	user_log = CustomUser.objects.get(username=user_log)
	
	aporte_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	aporte_inicial = AporteMensual.objects.get(aporte_mensual_deno='AMI')

	context = {
		'user_log': user_log,
		'aporte_actual': aporte_actual,
		'aporte_inicial': aporte_inicial
	}

	return context

def generar_historial_afil(request, user_log):

	try:

		aporte_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')
		aporte_inicial = AporteMensual.objects.get(aporte_mensual_deno='AMI')

		user_log = CustomUser.objects.get(username=user_log)

		afiliado = CustomUser.objects.get(username=user_log)

		historial = AporteAfiliado.objects.filter(
							afiliado_id=afiliado.id
							).order_by('-fecha_pago')
		
		# Configuración para el espacio de paginación
		paginator = Paginator(historial, 15)  # Mostrará hasta 15 operaciones por pág.
		page = request.GET.get('page')
		historial = paginator.get_page(page)

		context = {
			'user_log': user_log,
			'historial': historial,
			'aporte_actual': aporte_actual,
			'aporte_inicial': aporte_inicial

		}

		return context

	except:
		context = {}

		return context


def generar_historial_afil_fil(request, user_log, ta):
	

	aporte_actual = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	aporte_inicial = AporteMensual.objects.get(aporte_mensual_deno='AMI')
	
	user_log = CustomUser.objects.get(username=user_log)
	
	aporte_mensual = AporteMensual.objects.get(aporte_mensual_deno='AMU')  # Tasa única de cobro por aporte mensual
	historial = AporteAfiliado.objects.filter(
							afiliado_id=user_log.id,
							aporte_mensual_afil=aporte_mensual.id
							).order_by('-fecha_pago')
										
	# Configuración para el espacio de paginación
	paginator = Paginator(historial, 15)  # Mostrará hasta 15 operaciones por pág.
	page = request.GET.get('page')
	historial = paginator.get_page(page)

	context = {
		'user_log': user_log,
		'historial': historial,
		'aporte_actual': aporte_actual,
		'aporte_inicial': aporte_inicial
	}

	return context
	
def generar_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html = template.render(context_dict)
	result = io.BytesIO()

	pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)

	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None

def enviar_comprobante(request, comprobante):

	aporte = AporteAfiliado.objects.get(comprobante=comprobante)
	afiliado = CustomUser.objects.get(username=aporte.afiliado)
	recaudador = CustomUser.objects.get(username=aporte.recaudador)
	directivos = CustomUser.objects.filter(groups__name='Directivo')

	try:
		etiq = 'APORTE MENSUAL'
		monto = aporte.aporte_mensual_afil.aporte_mensual
	
	except:
		if aporte.aporte_dona_afil != '0':
			etiq = 'DONACIÓN'
			monto = aporte.aporte_dona_afil
		else:
			etiq = 'APORTE POR CERTIFICACIÓN'
			monto = aporte.aporte_certif_afil.aporte_certificacion

	destinatarios = [afiliado.email]

	for d in directivos:
		destinatarios.append(d.email)

	try:
		# CONTENIDO DEL CORREO
		asunto = f'COMPROBANTE POR {etiq}'
		msj = f'''
		SE HA PROCESADO UN PAGO POR {etiq}:

		COLEGIADO USERNAME: {afiliado.username}
		COLEGIADO C.I.: {afiliado.ci}
		COLEGIADO MATRÍCULA: {afiliado.matricula}

		RECAUDADOR USERNAME: {recaudador.username}
		RECAUDADOR C.I.: {recaudador.ci}
		RECAUDADOR MATRÍCULA: {recaudador.matricula}
		
		MONTO: {monto} B.s
		N° COMPROBANTE: {comprobante}
		TALONARIO: {aporte.talonario}
		FECHA DE PAGO: {aporte.fecha_pago}
		'''

		context = {
			'comprobante': comprobante,
			'talonario': aporte.talonario,
			'etiqueta': etiq,
			'afiliado': afiliado.username,
			'afiliado_ci': afiliado.ci,
			'afiliado_mat': afiliado.matricula,
			'recaudador': recaudador.username,
			'recaudador_ci': recaudador.ci,
			'recaudador_mat': recaudador.matricula,
			'monto': monto,
			'fecha_pago': aporte.fecha_pago

		}

		template = get_template('ProyectoApp/comprobante.html')
		html = template.render(context)
		result = io.BytesIO()
		pdf = pisa.pisaDocument(io.BytesIO(html.encode('ISO-8859-1')), result)
	
		msg = EmailMultiAlternatives(asunto, msj, EMAIL_HOST_USER, destinatarios)
		
		file_to_be_sent = result.getvalue()
		
		msg.attach(
			f'comprobante_{aporte.fecha_pago}.pdf',
			file_to_be_sent,
			'application/pdf')

		msg.send()

		return 1  # ENVIO CORRECTAMENTE
	
	except Exception as e:

		return e # ENVIO FALLO


def recaud_mes(request, user_log, tam):
	
	start_date = datetime.date.today().replace(day=1)  # Primer día del mes actual
	end_date = datetime.datetime.now().date()  # Fecha actual

	user_log = CustomUser.objects.get(username=user_log)
	
	tipo_factura = AporteMensual.objects.get(aporte_mensual_deno=tam)
	
	fact_amu = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	fact_ami = AporteMensual.objects.get(aporte_mensual_deno='AMI')

	cobros = AporteAfiliado.objects.filter(
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date]
			).order_by('-fecha_pago')

	fact_cobradas = len(cobros)

	paginator = Paginator(cobros, 15)  # Mostrará hasta 15 cobros por pág.
	page = request.GET.get('page')
	cobros = paginator.get_page(page)
		
	context = {
		'user_log': user_log,
		'cobros': cobros,
		'fact_cobradas': fact_cobradas,
		'monto_unit': tipo_factura.aporte_mensual,
		'monto_recaudado_total': fact_cobradas * int(tipo_factura.aporte_mensual),
		'tam': tam,
		'mes': True,
		'fechas': False,
		'fact_amu': fact_amu,
		'fact_ami': fact_ami
	}

	return context

def reporte_fechas(request, user_log, tam, start_date, end_date):
	
	user_log = CustomUser.objects.get(username=user_log)
	
	tipo_factura = AporteMensual.objects.get(aporte_mensual_deno=tam)
	
	fact_amu = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	fact_ami = AporteMensual.objects.get(aporte_mensual_deno='AMI')

	cobros = AporteAfiliado.objects.filter(
			aporte_mensual_afil=tipo_factura.id,
			fecha_pago__range=[start_date, end_date]
			).order_by('-fecha_pago')

	fact_cobradas = len(cobros)

	paginator = Paginator(cobros, 15)  # Mostrará hasta 15 cobros por pág.
	page = request.GET.get('page')
	cobros = paginator.get_page(page)
		
	context = {
		'user_log': user_log,
		'cobros': cobros,
		'fact_cobradas': fact_cobradas,
		'monto_unit': tipo_factura.aporte_mensual,
		'monto_recaudado_total': fact_cobradas * int(tipo_factura.aporte_mensual),
		'tam': tam,
		'mes': False,
		'fechas': True,
		'fact_amu': fact_amu,
		'fact_ami': fact_ami,
		'start_date': start_date,
		'end_date': end_date
	}

	return context
