from django.urls import path
from django.contrib.auth.decorators import login_required
from ProyectoApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	# VISTA INICIAL O INDEX DEL SITIO WEB
	path('', views.Inicio.as_view(), name='inicio'),
	
	# VISTAS DE REGISTRO/LOGIN/LOGOUT	
	path('accounts/login/', views.Login.as_view(), name='login'),
	path('checkuser/', login_required(views.ComprobarUsuario.as_view()), name='check-user'),
	path('logout/', login_required(views.logout_usuario), name='logout'),

	# VISTAS DIRECTIVO
	path('directivo-bienvenida/', login_required(views.DirectivoBienvenida.as_view()), name='directivo-bienvenida'),
	path('directivo<user_log>/', login_required(views.DirectivoDashboard.as_view()), name='directivo-dashboard'),
	path('directivo<user_log>/afiliados/', login_required(views.DirectivoDashboardAfiliados.as_view()), name='directivo-dashboard-afiliados'),
	path('dire41d4ctivoafildesh<user_log>/afiliados/', login_required(views.DirectivoDashboardAfiliadosDesh.as_view()), name='directivo-dashboard-afiliados-desh'),
	path('direcregistrec<user_log>/', login_required(views.DirectivoRegistroRecaudador.as_view()), name='directivo-registrar-recaudador'),
	path('direcregistafil<user_log>/', login_required(views.DirectivoRegistroAfiliado.as_view()), name='directivo-registrar-afiliado'),
	path('directivfdsfofiltci<user_log>/', login_required(views.DirectivoFiltrarUsuarioCI.as_view()), name='directivo-filtrar-ci'),
	path('directsfsfsivofiltmat<user_log>/', login_required(views.DirectivoFiltrarUsuarioMAT.as_view()), name='directivo-filtrar-mat'),
	path('directsfsfsivofiltapellpat<user_log>/', login_required(views.DirectivoFiltrarUsuarioApellPat.as_view()), name='directivo-filtrar-apell-pat'),
	path('directivofilt/<user_log>/<user_filt>/', login_required(views.DirectivoDashboardFiltrado.as_view()), name='directivo-dashboard-filtrado'),
	path('direcmoddatos/<user_log>/', login_required(views.DirectivoModDatos.as_view()), name='directivo-mod-datos'),
	path('direcmodclave/<user_log>/', login_required(views.DirectivoModClave.as_view()), name='directivo-mod-clave'),
	path('direcmodfoto/<user_log>/', login_required(views.DirectivoModFoto.as_view()), name='directivo-mod-foto'),
	path('direcsdasdastivoasdasdver/<user_log>/<usuario>/', login_required(views.DirectivoVerUsuario.as_view()), name='directivo-ver-usuario'),
	path('dadasdainfo<user_log>/', login_required(views.DirectivoInfo.as_view()), name='directivo-info'),
	path('directivoverrecaud/<user_log>/<recaudador>/<tam>/<th>/<start_date>/<end_date>/', login_required(views.DirectivoHistorialRecaudador.as_view()), name='directivo-historial-recaudador'),
	path('directivoverafil/<user_log>/<afiliado>/<tam>/<th>/<start_date>/<end_date>/', login_required(views.DirectivoHistorialAfiliado.as_view()), name='directivo-historial-afiliado'),
	path('direccleanuser/<user_log>/<usuario>/', login_required(views.DirectivoEliminarUsuario.as_view()), name='eliminar-usuario'),
	path('directverkardex/<user_log>/<user_filt>/', login_required(views.DirectivoVerKardex.as_view()), name='directivo-ver-kardex'),
	path('directactdatos/<user_log>/<user_filt>/', login_required(views.DirectivoActDatos.as_view()), name='directivo-act-datos'),
	path('directsfsfsivofiltcomp<user_log>/', login_required(views.DirectivoFiltrarComprobante.as_view()), name='directivo-filtrar-comp'),
	path('directsfsfsivofilttalon<user_log>/', login_required(views.DirectivoFiltrarTalonario.as_view()), name='directivo-filtrar-talon'),
	path('directivo2detalles/<user_log>/<comprobante>', login_required(views.DirectivoDetalles.as_view()), name='directivo-detalles'),
	path('dire41d4ctivoafildeudas<user_log>/afiliados/', login_required(views.DirectivoDashboardAfiliadosDeudas.as_view()), name='directivo-dashboard-afiliados-deudas'),
	path('directexphistoryrecaud/<user_log>/<user_filt>/<tam>/<mes>/<start_date>/<end_date>/', login_required(views.DirectivoExportarHistorialRecaud.as_view()), name='directivo-exp-historial-recaud'),
	path('directexphistoryafil/<user_log>/<user_filt>/<tam>/<mes>/<start_date>/<end_date>/', login_required(views.DirectivoExportarHistorialAfil.as_view()), name='directivo-exp-historial-afil'),
	path('directsendhistoryrecaud/<user_log>/<user_filt>/<th>/<tam>/<mes>/<start_date>/<end_date>/', login_required(views.DirectivoEnviarHistorialRecaud.as_view()), name='directivo-enviar-historial-recaud'),
	path('directsendhistoryafil/<user_log>/<user_filt>/<th>/<tam>/<mes>/<start_date>/<end_date>/', login_required(views.DirectivoEnviarHistorialAfil.as_view()), name='directivo-enviar-historial-afil'),
	path('directgetfechas/<user_log>/<user_filt>/<tam>/<th>/', login_required(views.DirectivoFechas.as_view()), name='directivo-fechas'),

	path('directvermikardex/<user_log>/', login_required(views.DirectivoVerMiKardex.as_view()), name='directivo-ver-mi-kardex'),

	path('directipoafil<user_log>/', login_required(views.DirectivoTipoAfiliado.as_view()), name='directivo-tipo-afiliado'),
	path('dihashdaskantg<user_log>/', login_required(views.DirectivoRegistroAfiliadoAntiguo.as_view()), name='directivo-registrar-afiliado-antiguo'),

	# VISTAS RECAUDADOR
	path('recaudador-bienvenida/', login_required(views.RecaudadorBienvenida.as_view()), name='recaudador-bienvenida'),
	path('recaudador/<user_log>/', login_required(views.RecaudadorDashboard.as_view()), name='recaudador-dashboard'),
	path('recaudadorfindci/<user_log>/', login_required(views.RecaudadorFiltrarUsuarioCI.as_view()), name='recaudador-filtrar-ci'),
	path('recaudadorfindmat/<user_log>/', login_required(views.RecaudadorFiltrarUsuarioMAT.as_view()), name='recaudador-filtrar-mat'),
	path('recaudadorget/<user_log>/<user_filt>/', login_required(views.RecaudadorDashboardFiltrado.as_view()), name='recaudador-dashboard-filtrado'),
	path('recaaudd0rafildesh<user_log>/afiliados/', login_required(views.RecaudadorDashboardAfiliadosDesh.as_view()), name='recaudador-dashboard-afiliados-desh'),
	path('reca2ud2a1dorget/<user_log>/', login_required(views.RecaudadorDashboardMisCobros.as_view()), name='recaudador-dashboard-mis-cobros'),
	path('re52da2a1getmonth/<user_log>/', login_required(views.RecaudadorDashboardMisCobrosMes.as_view()), name='recaudador-dashboard-mis-cobros-mes'),
	path('re52da2a1getfechas/<user_log>/', login_required(views.RecaudadorDashboardMisCobrosFechas.as_view()), name='recaudador-dashboard-mis-cobros-fechas'),
	path('recaudad2detalles/<user_log>/<comprobante>', login_required(views.RecaudadorDetalles.as_view()), name='recaudador-detalles'),
	path('recaudadormoddatos/<user_log>/', login_required(views.RecaudadorModDatos.as_view()), name='recaudador-mod-datos'),
	path('recaudadormodclave/<user_log>/', login_required(views.RecaudadorModClave.as_view()), name='recaudador-mod-clave'),
	path('recaudmodfoto/<user_log>/', login_required(views.RecaudadorModFoto.as_view()), name='recaudador-mod-foto'),
	path('recaudadorver/<user_log>/<usuario>/', login_required(views.RecaudadorVerUsuario.as_view()), name='recaudador-ver-usuario'),
	path('recaudadorcobrar/<user_log>/<usuario><int:ta>/', login_required(views.RecaudadorCobrar.as_view()), name='recaudador-cobrar'),
	path('recaudadorcobrarconfdatos/<user_log>/<usuario><int:ta>/<talon>/<fecha_pago>/<etiq>/<numero_recibo>', login_required(views.RecaudadorCobroConfirmarDatos.as_view()), name='recaudador-cobro-confirmar-datos'),
	path('recaudadorcobromult/<user_log>/<usuario>/', login_required(views.RecaudadorCobroMultiple.as_view()), name='recaudador-cobro-multiple'),
	path('recaudadorcobromultefect/<user_log>/<usuario>/<fecha_pago>/<int:cant>/<tam>/<talon>/<numero_recibo>', login_required(views.RecaudadorCobroMultipleEfect.as_view()), name='recaudador-cobro-multiple-efect'),
	path('recaudadorcobroefectuado/<user_log>/<comprobante>/', login_required(views.RecaudadorCobroEfectuado.as_view()), name='recaudador-cobro-efectuado'),
	path('recaudainfo<user_log>/', login_required(views.RecaudadorInfo.as_view()), name='recaudador-info'),
	path('recaudaviewhistory/<user_log>/<afiliado>/<tam>/<th>/<start_date>/<end_date>/', login_required(views.RecaudadorVerHistorial.as_view()), name='recaudador-ver-historial'),
	path('recaudsendhistoryafil/<user_log>/<user_filt>/<th>/<tam>/<mes>/<start_date>/<end_date>/', login_required(views.RecaudadorEnviarHistorialAfil.as_view()), name='recaudador-enviar-historial-afil'),
	path('recaudexphistoryafil/<user_log>/<user_filt>/<tam>/<mes>/<start_date>/<end_date>/', login_required(views.RecaudadorExportarHistorialAfil.as_view()), name='recaudador-exp-historial-afil'),
	path('recaudgetfechas/<user_log>/<user_filt>/<tam>/<th>/', login_required(views.RecaudadorFechas.as_view()), name='recaudador-fechas'),
	path('recdaexpmiscobros/<user_log>/', login_required(views.RecaudadorExportarMisCobros.as_view()), name='recaudador-exp-mis-cobros'),
	path('recdaexpmiscobrosmes/<user_log>/', login_required(views.RecaudadorExportarMisCobrosMes.as_view()), name='recaudador-exp-mis-cobros-mes'),
	path('recdaexpmiscobrosfechas/<user_log>/<start_date>/<end_date>/', login_required(views.RecaudadorExportarMisCobrosFechas.as_view()), name='recaudador-exp-mis-cobros-fechas'),
	path('recaudverkardex/<user_log>/<user_filt>/', login_required(views.RecaudadorVerKardex.as_view()), name='recaudador-ver-kardex'),
	path('recauddorfiltcomp<user_log>/', login_required(views.RecaudadorFiltrarComprobante.as_view()), name='recaudador-filtrar-comp'),
	path('recauddorfilttalon<user_log>/', login_required(views.RecaudadorFiltrarTalonario.as_view()), name='recaudador-filtrar-talon'),
	path('recaudregistafil<user_log>/', login_required(views.RecaudadorRegistroAfiliado.as_view()), name='recaudador-registrar-afiliado'),
	path('reccauddd0rfiltapellpat<user_log>/', login_required(views.RecaudadorFiltrarUsuarioApellPat.as_view()), name='recaudador-filtrar-apell-pat'),
	path('recaudadregiscobro<user_log>/', login_required(views.RecaudadorRegistrarCobro.as_view()), name='recaudador-registrar-cobro'),
	path('recaudactdatos/<user_log>/<user_filt>/', login_required(views.RecaudadorActDatos.as_view()), name='recaudador-act-datos'),
	path('recauddafildeudas<user_log>/afiliados/', login_required(views.RecaudadorDashboardAfiliadosDeudas.as_view()), name='recaudador-dashboard-afiliados-deudas'),
	path('recaudvermikardex/<user_log>/', login_required(views.RecaudadorVerMiKardex.as_view()), name='recaudador-ver-mi-kardex'),

	path('recaudtipoafil<user_log>/', login_required(views.RecaudadorTipoAfiliado.as_view()), name='recaudador-tipo-afiliado'),
	path('rehasdamaafilant<user_log>/', login_required(views.RecaudadorRegistroAfiliadoAntiguo.as_view()), name='recaudador-registrar-afiliado-antiguo'),

	path('recaudcleanuser/<user_log>/<usuario>/', login_required(views.RecaudadorEliminarUsuario.as_view()), name='recaudador-eliminar-usuario'),
	path('eliasdmapfasforte/<user_log>/<comprobante>/', login_required(views.EliminarAporte.as_view()), name='eliminar-aporte'),
	path('recaudadestemes/<user_log>/<tam>/', login_required(views.RecaudEsteMes.as_view()), name='recaudado-este-mes'),
	path('reporteanual/<user_log>/<tam>/', login_required(views.ReporteAnual.as_view()), name='reporte-anual'),
	path('reportefechas/<user_log>/<tam>/', login_required(views.ReporteFechas.as_view()), name='reporte-fechas'),
	path('reportefechas/<user_log>/<tam>/<start_date>/<end_date>/', login_required(views.ReporteFechasListo.as_view()), name='reporte-fechas-listo'),

	path('exportarreporteafildeud/<user_log>/', login_required(views.ExportarAfiliadosDeudores.as_view()), name='exportar-afiliados-deudores'),

	# VISTAS AFILIADO
	path('afiliado-bienvenida/', login_required(views.AfiliadoBienvenida.as_view()), name='afiliado-bienvenida'),
	path('afiliado-bienvenida/<user_log>/', login_required(views.AfiliadoDashboard.as_view()), name='afiliado-dashboard'),
	path('afiliadohistorial/<user_log>/', login_required(views.AfiliadoHistorial.as_view()), name='afiliado-historial'),
	path('afiliadohistorialfil/<user_log><ta>/', login_required(views.AfiliadoHistorialFiltrado.as_view()), name='afiliado-historial-filtrado'),
	path('afiliadomodclave/<user_log>/', login_required(views.AfiliadoModClave.as_view()), name='afiliado-mod-clave'),
	path('afiliadodetalles/<user_log>/<comprobante>', login_required(views.AfiliadoDetalles.as_view()), name='afiliado-detalles'),
	path('minfo<user_log>/', login_required(views.AfiliadoInfo.as_view()), name='afiliado-info'),
	path('modificarusuario/<user_log>/<usuario>/', login_required(views.ModificarUsuario.as_view()), name='modificar-usuario'),
	path('afasddoviewhistory/<user_log>/<tam>/<th>/<start_date>/<end_date>/', login_required(views.AfiliadoVerHistorial.as_view()), name='afiliado-ver-historial'),
	path('afiliadoexphistory/<user_log>/<tam>/<th>/<start_date>/<end_date>/', login_required(views.AfiliadoExportarHistorial.as_view()), name='afiliado-exp-historial'),
	path('afilgetfechas/<user_log>/<tam>/<th>/', login_required(views.AfiliadoFechas.as_view()), name='afiliado-fechas'),
	path('afilermikardex/<user_log>/', login_required(views.AfiliadoVerMiKardex.as_view()), name='afiliado-ver-mi-kardex'),

	path('enviarcomprobante/<comprobante>/', login_required(views.EnviarComprobante.as_view()), name='enviar-comprobante'),
	path('generarpdf<comprobante>/', login_required(views.GenerarPDF.as_view()), name='generar-pdf'),
	path('printkardex<user_filt>/', login_required(views.ImprimirKardex.as_view()), name='imprimir-kardex'),
]#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
