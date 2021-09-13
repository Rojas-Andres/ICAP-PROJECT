from django.contrib import admin
from .models import CustomUser, RegistrarUsuario, AporteMensual, AporteAfiliado, AporteCertificacion
from .forms import CustomUserCreationForm
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
	model = CustomUser
	add_form = CustomUserCreationForm

	UserAdmin.add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('username', 'email', 'matricula', 'ci', 'password1', 'password2',)
		}),
	)

	
	fieldsets = (
		*UserAdmin.fieldsets,
		(
			'INFORMACIÓN ADICIONAL',
			{
				'fields': (
					'foto',
					'apell_pat',
					'apell_mat',
					'ci',
					'direcc',
					'telefono',
					'celular',
					'matricula',
					'fecha_registro',
					'usuario_vivo',
					'estado_usuario',
					# CAMPOS NUEVOS (22-03-21):
					'lugar_nac',
					'fecha_nac',
					'est_civil',
					'univ_estud',
					'fecha_tg',
					'univ_lic',
					'fecha_ol',
					'fecha_tit_pn',
					'ent_pub',
					'cargos_judic',
					'cargos_admin_pub',
					'cargos_priv_otras',
					'tiempo_ejec_prof_sd',
					'cargo_actual',
					'prod_jur',
					'estud_espec',
					'recon_obt',
					'asist_event_inter',
					'inst_aseg',
					'beneficiarios',
					'espec_ejer_der',
					'direc_ofic',
					'tel_ofic',
					'observ',
				)
			}
		)
	)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(RegistrarUsuario)
admin.site.register(AporteMensual)
admin.site.register(AporteAfiliado)
admin.site.register(AporteCertificacion)
