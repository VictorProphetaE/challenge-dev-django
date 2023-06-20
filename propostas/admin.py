from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib import admin
from django.db import models
from .models import User, Proposta, CampoDinamico, ValorCampoDinamico
from django import forms
from django.utils.html import format_html
from django.forms.models import BaseInlineFormSet, inlineformset_factory

# Obtém o modelo de usuário personalizado definido no projeto
custom_user_model = get_user_model()

class CampoDinamicoForm(forms.ModelForm):
    custom_nome = forms.CharField(label='Nome Personalizado', required=False)

    class Meta:
        model = CampoDinamico
        fields = '__all__'
        exclude = []

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        custom_nome = cleaned_data.get('custom_nome')

        if not nome and not custom_nome:
            raise forms.ValidationError('É necessário fornecer um nome para o campo.')

        if nome == 'CUSTOM' and custom_nome:
            cleaned_data['nome'] = custom_nome

        return cleaned_data

# Formulário personalizado para criação de usuários
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = custom_user_model
        fields = ("username", "email", "password1", "password2", "administrador")

# Admin personalizado para o modelo de usuário personalizado 
class CustomUserAdmin(UserAdmin):
    model = custom_user_model

    list_display = ("id", "email", "username", "date_joined", "last_login", "administrador")
    list_editable = ["administrador"]
    search_fields = ("email", "username",)
    readonly_fields = ("date_joined", "last_login",)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "administrador", "password1", "password2"),
        }),
    )
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    add_form = CustomUserCreationForm

class CampoDinamicoAdmin(admin.ModelAdmin):
    list_display = ('get_nome_display', 'tipo', 'tamanho_maximo', 'opcoes_choices', 'min_value', 'max_value', 'custom_nome')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=obj, **kwargs)
        if obj:
            form.base_fields.pop('nome', None)
        return form

    def save_model(self, request, obj, form, change):
        if not obj.nome:
            obj.nome = 'CUSTOM'
        super().save_model(request, obj, form, change)

class ValorCampoDinamicoForm(forms.ModelForm):
    campo_dinamico = forms.ModelChoiceField(queryset=CampoDinamico.objects.none())

    def __init__(self, *args, **kwargs):
        campo_dinamico_queryset = kwargs.pop('campo_dinamico_queryset', None)
        super().__init__(*args, **kwargs)
        if campo_dinamico_queryset is not None:
            self.fields['campo_dinamico'].queryset = campo_dinamico_queryset

        # Adicionar a descrição do campo como ajuda (help_text)
        for field_name, field in self.fields.items():
            if field_name != 'campo_dinamico':
                campo_dinamico = CampoDinamico.objects.filter(nome=field_name).first()
                if campo_dinamico:
                    field.help_text = f"{campo_dinamico.descricao} ({campo_dinamico.tipo})"

    class Meta:
        model = ValorCampoDinamico
        fields = '__all__'

# Criação de um conjunto de formulários inline para ValorCampoDinamico
ValorCampoDinamicoFormSet = inlineformset_factory(
    Proposta, ValorCampoDinamico, form=ValorCampoDinamicoForm, extra=0
)

# Criação de um conjunto de formulários inline para ValorCampoDinamico
class ValorCampoDinamicoInline(admin.TabularInline):
    model = ValorCampoDinamico
    extra = 0
    formset = inlineformset_factory(Proposta, ValorCampoDinamico, formset=ValorCampoDinamicoFormSet, fields='__all__')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.campo_dinamico_queryset = CampoDinamico.objects.filter(
            tipo__in=['CharField', 'IntegerField', 'FloatField', 'PhoneField', 'DateTimeField', 'DateOfBirth', 'EmailField', 'BooleanField']
        )
        return formset

    def get_extra(self, request, obj=None, **kwargs):
        extra = super().get_extra(request, obj=obj, **kwargs)
        if obj:
            campos_dinamicos = CampoDinamico.objects.filter(
                tipo__in=['CharField', 'IntegerField', 'FloatField', 'PhoneField', 'DateTimeField', 'DateOfBirth', 'EmailField', 'BooleanField']
            )
            extra = max(extra, campos_dinamicos.count() - self.model.objects.filter(proposta=obj).count())
        return extra
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'valor':
            formfield.widget.description = db_field.get_internal_type()
        return formfield

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj=obj)
        if obj:
            fields = [f.name for f in self.model._meta.get_fields()]
            fields.remove('id')

            # Adicionar novo fieldset para descrição dos campos
            description_fields = [(f.description,) for f in self.form.base_fields.values() if f.name in fields]
            fieldsets.append(('Descrição dos Campos', {'fields': description_fields}))

        return fieldsets

class PropostaAdmin(admin.ModelAdmin):
    inlines = [ValorCampoDinamicoInline]

    def campo_dinamico_(self, obj):
        valores = []
        valores_campo_dinamico = obj.valores_campo_dinamico.all()
        for valor in valores_campo_dinamico:
            campo_dinamico = CampoDinamico.objects.get(pk=valor.campo_dinamico_id)
            valor_display = f"{campo_dinamico.tipo}: {valor.get_valor()}"
            valores.append(valor_display)
        return format_html("<br>".join(valores))

    campo_dinamico_.short_description = 'Valores campo dinâmicos'

    list_display = ('campo_dinamico_','status')

# Registro dos modelos e admin personalizados no painel de administração
admin.site.register(Proposta, PropostaAdmin)
admin.site.register(custom_user_model, CustomUserAdmin)
admin.site.register(CampoDinamico, CampoDinamicoAdmin)