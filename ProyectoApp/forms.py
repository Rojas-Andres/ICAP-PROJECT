from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django import forms

import datetime

from .models import CustomUser, RegistrarUsuario, AporteAfiliado, AporteMensual


class CustomUserCreationForm(UserCreationForm):
	
	class Meta:
		model = CustomUser
		fields = '__all__'

class FormularioLogin(AuthenticationForm):
	def __init__(self, *args, **kwargs):
		super(FormularioLogin, self).__init__(*args, **kwargs)
		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'Nombre de usuario'
		self.fields['password'].widget.attrs['class'] = 'form-control'
		self.fields['password'].widget.attrs['placeholder'] = 'Contraseña'

class FormularioFechas(forms.Form):
	
	fecha1 = forms.DateField(widget=forms.SelectDateWidget(years=range(2010, datetime.date.today().year+50)))
	fecha2 = forms.DateField(widget = forms.SelectDateWidget(years=range(2010, datetime.date.today().year+50)))

class FormularioYear(forms.Form):
	YEAR_CHOICES = []

	for y in range(1970, (datetime.datetime.now().year + 1)):
		YEAR_CHOICES.append((y, y))


	YEAR_CHOICES.sort(reverse=True)

	year = forms.TypedChoiceField(choices=YEAR_CHOICES, coerce=str)

class FormularioCobroMult(forms.Form):
	
	CHOICES = (
		(2, '2'),
		(3, '3'),
		(4, '4'),
		(5, '5'),
		(6, '6'),
		(7, '7'),
		(8, '8'),
		(9, '9'),
		(10, '10'),
		(11, '11'),
		(12, '12'),
		)

	amu = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	#ami = AporteMensual.objects.get(aporte_mensual_deno='AMI')

	CHOICESAPORTES = (
		(amu, f'{amu.aporte_mensual} Bs.'),
		#(ami, f'{ami.aporte_mensual} Bs.'),
		)

	aporte_mensual_deno = forms.TypedChoiceField(choices=CHOICESAPORTES, coerce=str)

	#cantidad = forms.TypedChoiceField(choices=CHOICES, coerce=str)
	cantidad = forms.CharField(
		widget=forms.TextInput(
			attrs={'class': 'mdl-textfield__input', 'type': 'number',}
			)
		)
	fecha_pago = forms.DateField(
		widget=forms.DateInput(
			attrs={'placeholder': datetime.datetime.now().date(), 'required': 'required'}
			)
		)
	talonario = forms.CharField(
		widget=forms.TextInput(
			attrs={'class': 'mdl-textfield__input', 'type': 'number',}
			)
		)


	numero_recibo =forms.CharField(
		widget=forms.TextInput(
			attrs={'class': 'mdl-textfield__input', 'type': 'number',}
			)
		)
class FormularioRegistrarCobro(forms.Form):
	
	CHOICES = (
		('C.I.', 'C.I.'),
		('N° Matrícula ICAP', 'N° Matrícula ICAP'),
		('Apellido Paterno', 'Apellido Paterno')
	)

	opcion = forms.TypedChoiceField(choices=CHOICES, coerce=str)
	
class FormularioRegistroUsuario(forms.ModelForm):
	
	CHOICES = (
		('Soltero (a)', 'Soltero (a)'),
		('Casado (a)', 'Casado (a)'),
		('Divorciado (a)', 'Divorciado (a)'),
	)

	est_civil = forms.TypedChoiceField(choices=CHOICES, coerce=str)

	CHOICES_ENT_PUB_PRI = (
		('ENTIDAD PÚBLICA', 'ENTIDAD PÚBLICA'),
		('ENTIDAD PRIVADA', 'ENTIDAD PRIVADA'),
	)

	ent_pub = forms.TypedChoiceField(choices=CHOICES_ENT_PUB_PRI, coerce=str)
	CHOICES_EXPEDIDO = ( 
		('CH','CH'),
		('LP','LP'),
		('CB','CB'),
		('OR','OR'),
		('PT','PT'),
		('TJ','TJ'),
		('SC','SC'),
		('BE','BE'),
		('PD','PD'),
	)

	expedido = forms.TypedChoiceField(choices=CHOICES_EXPEDIDO, coerce=str)
	class Meta:
		model = RegistrarUsuario
		fields = '__all__' 
		exclude = ['password_new1', 'password_new2']

		widgets = {

			'foto': forms.FileInput(
			),
		

			'lugar_nac': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'fecha_nac': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'				
				}
			),


			'univ_estud': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'fecha_tg': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'
					
				}
			),

			'univ_lic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'fecha_ol': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'
					
				}
			),

			'fecha_tit_pn': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'
					
				}
			),

			
			'cargos_judic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'cargos_admin_pub': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'cargos_priv_otras': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'tiempo_ejec_prof_sd': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'cargo_actual': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'prod_jur': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

		

			'estud_espec': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'recon_obt': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'asist_event_inter': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'inst_aseg': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'beneficiarios': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'espec_ejer_der': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'direc_ofic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'tel_ofic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'direcc': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'telefono': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'celular': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'observ': forms.Textarea(
				
				attrs = {
					'class': 'form-control',
					'rows': '6',
					'placeholder': 'Escriba aquí las observaciones',
				}

			),

			'first_name': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					

				}
			),

			'apell_pat': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'apell_mat': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

		
			'matricula': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number',
					
				}
			),

			'ci': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'email': forms.EmailInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'username': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'text',
					'pattern': r'-?[a-z]*(\.[0-9]+)?',
					
				}
			),

			'password1': forms.PasswordInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'password2': forms.PasswordInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			
			'fecha_registro': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': timezone.now()
					
				}
			),


			'usuario_vivo': forms.CheckboxInput(
				
				attrs = {
					
				}
			),

			'estado_usuario': forms.CheckboxInput(
				
				attrs = {
					
				}
			),

		}

class FormularioRegistroAfiliadoAntiguo(forms.ModelForm):
	
	cant_aportes_iniciales = forms.CharField(
		widget=forms.TextInput(
			attrs={'class': 'mdl-textfield__input', 'type': 'number',}
			)
		)
	
	talonario = forms.CharField(
		widget=forms.TextInput(
			attrs={'class': 'mdl-textfield__input', 'type': 'number',}
			)
		)

	CHOICES = (
		('Soltero (a)', 'Soltero (a)'),
		('Casado (a)', 'Casado (a)'),
		('Divorciado (a)', 'Divorciado (a)'),
		)
	
	CHOICES_EXPEDIDO = ( 
		('CH','CH'),
		('LP','LP'),
		('CB','CB'),
		('OR','OR'),
		('PT','PT'),
		('TJ','TJ'),
		('SC','SC'),
		('BE','BE'),
		('PD','PD'),
	)

	expedido = forms.TypedChoiceField(choices=CHOICES_EXPEDIDO, coerce=str)

	est_civil = forms.TypedChoiceField(choices=CHOICES, coerce=str)

	CHOICES_ENT_PUB_PRI = (
		('ENTIDAD PÚBLICA', 'ENTIDAD PÚBLICA'),
		('ENTIDAD PRIVADA', 'ENTIDAD PRIVADA'),
	)

	ent_pub = forms.TypedChoiceField(choices=CHOICES_ENT_PUB_PRI, coerce=str)

	class Meta:
		model = RegistrarUsuario
		fields = '__all__' 
		exclude = ['password_new1', 'password_new2']

		widgets = {

			'foto': forms.FileInput(
			),
		

			'lugar_nac': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'fecha_nac': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'				
				}
			),

	
			'univ_estud': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'fecha_tg': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'
					
				}
			),

			'univ_lic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'fecha_ol': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'
					
				}
			),

			'fecha_tit_pn': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'
					
				}
			),

			
			'cargos_judic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'cargos_admin_pub': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'cargos_priv_otras': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'tiempo_ejec_prof_sd': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'cargo_actual': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'prod_jur': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

		
			'estud_espec': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'recon_obt': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'asist_event_inter': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'inst_aseg': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'beneficiarios': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'espec_ejer_der': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'direc_ofic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'tel_ofic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'direcc': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'telefono': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'celular': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'observ': forms.Textarea(
				
				attrs = {
					'class': 'form-control',
					'rows': '6',
					'placeholder': 'Escriba aquí las observaciones',
				}

			),

			'first_name': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					

				}
			),

			'apell_pat': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'apell_mat': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'matricula': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number',
					
				}
			),

			'ci': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'email': forms.EmailInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'username': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'text',
					'pattern': r'-?[a-z]*(\.[0-9]+)?',
					
				}
			),

			'password1': forms.PasswordInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'password2': forms.PasswordInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			
			'fecha_registro': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': timezone.now()
					
				}
			),


			'usuario_vivo': forms.CheckboxInput(
				
				attrs = {
					
				}
			),

			'estado_usuario': forms.CheckboxInput(
				
				attrs = {
					
				}
			),

		}

class FormularioModificarDatos(forms.ModelForm):
	
	ci = forms.CharField(
		widget=forms.TextInput(
			attrs={'class': 'mdl-textfield__input', 'type': 'number',}
			)
		)
	
	CHOICES_ENT_PUB_PRI = (
		('ENTIDAD PÚBLICA', 'ENTIDAD PÚBLICA'),
		('ENTIDAD PRIVADA', 'ENTIDAD PRIVADA'),
	)

	ent_pub = forms.TypedChoiceField(choices=CHOICES_ENT_PUB_PRI, coerce=str)

	class Meta:
		model = CustomUser
		fields = [
			'first_name', 'apell_pat', 'apell_mat',
			'telefono', 'celular', 'direcc',
			'email', 'lugar_nac', 'fecha_nac',
			'est_civil', 'univ_estud', 'fecha_tg',
			'univ_lic', 'fecha_ol', 'fecha_tit_pn',
			'cargos_judic', 'cargos_admin_pub', 'cargos_priv_otras',
			'tiempo_ejec_prof_sd', 'cargo_actual', 'prod_jur','estud_espec', 'recon_obt',
			'asist_event_inter', 'inst_aseg', 'beneficiarios',
			'espec_ejer_der', 'direc_ofic', 'tel_ofic',
		]
		
		widgets = {

			'first_name': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					

				}
			),

			'apell_pat': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'apell_mat': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'lugar_nac': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'fecha_nac': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'				
				}
			),

		
			'est_civil': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'univ_estud': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'fecha_tg': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'
					
				}
			),

			'univ_lic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'fecha_ol': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'
					
				}
			),

			'fecha_tit_pn': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'
					
				}
			),

			
			'cargos_judic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'cargos_admin_pub': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'cargos_priv_otras': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'tiempo_ejec_prof_sd': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'cargo_actual': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'prod_jur': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),


			'estud_espec': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'recon_obt': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'asist_event_inter': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'inst_aseg': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'beneficiarios': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'espec_ejer_der': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'direc_ofic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'tel_ofic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'direcc': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'telefono': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'celular': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'email': forms.EmailInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),
		
		}

class FormularioModificarClave(forms.ModelForm):
	class Meta:
		model = RegistrarUsuario
		fields = ['password1', 'password2', 'password_new1', 'password_new2']
		
		widgets = {

			'password1': forms.PasswordInput(
				
				attrs = {
					'class': 'mdl-textfield__input',

				}
			),

			'password2': forms.PasswordInput(
				
				attrs = {
					'class': 'mdl-textfield__input',

				}
			),

			'password_new1': forms.PasswordInput(
				
				attrs = {
					'class': 'mdl-textfield__input',

				}
			),

			'password_new2': forms.PasswordInput(
				
				attrs = {
					'class': 'mdl-textfield__input',

				}
			),
		}

class FormularioSubirFoto(forms.ModelForm):
	class Meta:
		model = CustomUser
		fields = ['foto']
		
		widgets = {
			'foto': forms.FileInput(
			),
		}

class FormularioModificarUsuario(forms.ModelForm):
	
	class Meta:
		model = RegistrarUsuario
		fields = ['matricula', 'ci', 'email', 'username', 'password1', 'fecha_registro', 'usuario_vivo']
		
		widgets = {

			'matricula': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'ci': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'Sin comas ni puntos',
					'type': 'number'
					
				}
			),

			'password1': forms.PasswordInput(
				
				attrs = {
					'class': 'mdl-textfield__input',

				}
			),

			'fecha_registro': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': timezone.now()
					
				}
			),

			'email': forms.EmailInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'username': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'text',
					'pattern': r'-?[a-z]*(\.[0-9]+)?',
					
				}
			),
			
			'usuario_vivo': forms.CheckboxInput(
				
				attrs = {
					
				}
			),
			
		}

class FormularioFiltrarUsuarioMAT(forms.ModelForm):
	class Meta:
		model = RegistrarUsuario
		fields = ['matricula'] 
		
		widgets = {

			'matricula': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

		}

class FormularioFiltrarUsuarioApellPat(forms.ModelForm):
	class Meta:
		model = RegistrarUsuario
		fields = ['apell_pat'] 
		
		widgets = {

			'apell_pat': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'text',
				}
			),

		}

class FormularioFiltrarUsuarioCI(forms.ModelForm):
	class Meta:
		model = RegistrarUsuario
		fields = ['ci'] 
		
		widgets = {

			'ci': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

		}

class FormularioFiltrarComprobante(forms.Form):
	
	comprobante = forms.CharField(
		widget=forms.TextInput(
			attrs={'class': 'mdl-textfield__input', 'type': 'number',}
			)
		)

class FormularioFiltrarTalonario(forms.Form):
	
	talonario = forms.CharField(
		widget=forms.TextInput(
			attrs={'class': 'mdl-textfield__input', 'type': 'number',}
			)
		)
	
	

class FormularioCobrarAM(forms.ModelForm):
	
	amu = AporteMensual.objects.get(aporte_mensual_deno='AMU')
	#ami = AporteMensual.objects.get(aporte_mensual_deno='AMI')

	CHOICES = (
		(amu, f'{amu.aporte_mensual} Bs.'),
		#(ami, f'{ami.aporte_mensual} Bs.'),
		)

	aporte_mensual_deno = forms.TypedChoiceField(choices=CHOICES, coerce=str)

	talonario = forms.CharField(
		widget=forms.TextInput(
			attrs={'class': 'mdl-textfield__input', 'type': 'number',}
			)
		)

	numero_recibo = forms.CharField(
	widget=forms.TextInput(
		attrs={'class': 'mdl-textfield__input', 'type': 'number',}
		)
	)
	
	class Meta:
		model = AporteAfiliado
		fields = ['fecha_pago', 'aporte_mensual_deno'] 

		widgets = {

			'fecha_pago': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': timezone.now()
					
				}
			),

		}

class FormularioCobrarAC(forms.ModelForm):
	talonario = forms.CharField(
		widget=forms.TextInput(
			attrs={'class': 'mdl-textfield__input', 'type': 'number',}
			)
		)

	class Meta:
		model = AporteAfiliado
		fields = ['fecha_pago'] 
		
		widgets = {

			'fecha_pago': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': timezone.now()
					
				}
			),

		}

class FormularioCobrarAD(forms.ModelForm):
	talonario = forms.CharField(
		widget=forms.TextInput(
			attrs={'class': 'mdl-textfield__input', 'type': 'number',}
			)
		)

	class Meta:
		model = AporteAfiliado
		fields = ['fecha_pago', 'aporte_dona_afil'] 
		
		widgets = {

			'fecha_pago': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': timezone.now()
					
				}
			),

			'aporte_dona_afil': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
				}
			),

		}

class FormularioActualizarDatos(forms.ModelForm):
	
	CHOICES = (
		('Soltero (a)', 'Soltero (a)'),
		('Casado (a)', 'Casado (a)'),
		('Divorciado (a)', 'Divorciado (a)'),
		)

	est_civil = forms.TypedChoiceField(choices=CHOICES, coerce=str)

	matricula = forms.CharField(
		widget=forms.TextInput(
			attrs={'class': 'mdl-textfield__input', 'type': 'number',}
			)
		
	)

	ci = forms.CharField(
		widget=forms.TextInput(
			attrs={'class': 'mdl-textfield__input', 'type': 'number',}
			)
		)

	CHOICES_ENT_PUB_PRI = (
		('ENTIDAD PÚBLICA', 'ENTIDAD PÚBLICA'),
		('ENTIDAD PRIVADA', 'ENTIDAD PRIVADA'),
	)

	ent_pub = forms.TypedChoiceField(choices=CHOICES_ENT_PUB_PRI, coerce=str)

	class Meta:
		model = CustomUser
		fields = [
			'foto', 'first_name', 'email', 'apell_pat',
			'apell_mat', 'lugar_nac', 'fecha_nac',
			 'est_civil', 'univ_estud', 'fecha_tg',
			'univ_lic', 'fecha_ol', 'fecha_tit_pn',
			'fecha_registro', 'cargos_judic', 'cargos_admin_pub',
			'cargos_priv_otras', 'tiempo_ejec_prof_sd', 'cargo_actual',
			'prod_jur',  'estud_espec', 'recon_obt',
			'asist_event_inter', 'inst_aseg', 'beneficiarios',
			'espec_ejer_der', 'direc_ofic', 'tel_ofic', 
			'direcc', 'telefono', 'celular', 'email', 'observ',
			'usuario_vivo', 'estado_usuario'
		]
		
		widgets = {

			'foto': forms.FileInput(
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'usuario_vivo': forms.CheckboxInput(
				
				attrs = {
					
				}
			),

			'estado_usuario': forms.CheckboxInput(
				
				attrs = {
					
				}
			),

			'first_name': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					

				}
			),

			'apell_pat': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'apell_mat': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'lugar_nac': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'fecha_nac': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'				
				}
			),


			'univ_estud': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'fecha_tg': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'
					
				}
			),

			'univ_lic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'fecha_ol': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'
					
				}
			),

			'fecha_tit_pn': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'
					
				}
			),

			'fecha_registro': forms.DateInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'placeholder': 'dd/mm/aaaa'
					
				}
			),

			'cargos_judic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'cargos_admin_pub': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'cargos_priv_otras': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'tiempo_ejec_prof_sd': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'cargo_actual': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'prod_jur': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'estud_espec': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'recon_obt': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'asist_event_inter': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'inst_aseg': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'beneficiarios': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'espec_ejer_der': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'direc_ofic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'tel_ofic': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'direcc': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),

			'telefono': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'celular': forms.TextInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					'type': 'number'
					
				}
			),

			'email': forms.EmailInput(
				
				attrs = {
					'class': 'mdl-textfield__input',
					
				}
			),
			
			'observ': forms.Textarea(
				
				attrs = {
					'class': 'form-control',
					'rows': '6',
					'placeholder': 'Escriba aquí las observaciones',
				}

			),

		}
