from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    administrador = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class CampoDinamico(models.Model):
    # Opções disponíveis para o campo 'tipo'
    TIPO_CHOICES = (
        ('CharField', 'CharField'),
        ('IntegerField', 'IntegerField'),
        ('FloatField', 'FloatField'),
        ('PhoneField', 'PhoneField'),
        ('GenderField', 'GenderField'),
        ('DateTimeField', 'DateTimeField'),
        ('DateOfBirth', 'DateOfBirth'),
        ('EmailField', 'EmailField'),
        ('BooleanField', 'BooleanField')
    )
    # Nomes predefinidos para os campos
    NOMES = (
        ('NOME','Nome Completo'),
        ('END','Endereco'),
        ('TEL','Telefone'),
        ('CEL','Celular'),
        ('NOMEPAI','Nome do Pai'),
        ('NOMEMAE','Nome da Mae'),
        ('EMAIL','Email'),
        ('CPF','CPF'),
        ('RG','RG'),
        ('GENERO','Genero'),
        ('DATA','Data Nascimento'),
        ('IDADE','Idade'),
        ('VALOR','Valor do Emprestimo Pretendido'),
        ('TOTAL','Total'),
        ('VALORP','Valor do Emprestimo Pagar'),
        ('JUROS','Juros'),
        ('PREST','Prestacao'),
        ('SALDO','Saldo'),
        ('AMORTI','Amortizacao'),
        ('CUSTOM','Customizado'),
    )
    
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    nome = models.CharField(max_length=50, choices=NOMES)
    min_value = models.FloatField(blank=True, null=True)
    max_value = models.FloatField(blank=True, null=True)
    opcoes_choices = models.TextField(blank=True, null=True, help_text="Informe as opções separadas por vírgula")
    custom_nome = models.CharField(max_length=50, blank=True, null=True)
    valor = models.CharField(max_length=255, blank=True, null=True)
    # RegexValidator para validar o formato de telefone
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="O número de telefone deve estar no formato: '+999999999'. Até 15 dígitos são permitidos."
    )
    # RegexValidator para validar o formato de e-mail
    email_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        message="Digite um endereço de e-mail válido."
    )
        
    def tamanho_maximo(self):
        # Retorna o tamanho máximo do campo se for do tipo 'CharField', caso contrário, retorna None
        if self.tipo == 'CharField':
            return 255
        return None

    def clean(self):
        super().clean()
        # Verificação para os tipos campos válidos
        if self.nome == 'EMAIL':
            if self.tipo not in ['EmailField', 'CharField']:
                raise ValidationError("Para o campo 'EMAIL', os tipos disponíveis são 'EmailField' ou 'CharField'.")
        elif self.nome == 'CPF':
            if self.tipo != 'CharField':
                raise ValidationError("Para o campo 'CPF', o tipo disponível é 'CharField'.")
        elif self.nome in ['NOME', 'END', 'NOMEPAI', 'NOMEMAE', 'RG', 'GENERO']:
            if self.tipo != 'CharField':
                raise ValidationError(f"Para o campo '{self.nome}', o tipo disponível é 'CharField'.")
        elif self.nome in ['TEL', 'CEL']:
            if self.tipo != 'PhoneField':
                raise ValidationError(f"Para o campo '{self.nome}', o tipo disponível é 'PhoneField'.")
        elif self.nome == 'DATA':
            if self.tipo != 'DateOfBirth':
                raise ValidationError(f"Para o campo '{self.nome}', o tipo disponível é 'DateOfBirth'.")
        elif self.nome == 'IDADE':
            if self.tipo != 'IntegerField':
                raise ValidationError(f"Para o campo '{self.nome}', o tipo disponível é 'IntegerField'.")
        elif self.nome in ['VALOR', 'VALORP', 'JUROS', 'PREST', 'SALDO', 'AMORTI']:
            if self.tipo != 'FloatField':
                raise ValidationError(f"Para o campo '{self.nome}', o tipo disponível é 'FloatField'.")
        elif self.nome == 'TOTAL':
            if self.tipo != 'IntegerField':
                raise ValidationError(f"Para o campo '{self.nome}', o tipo disponível é 'IntegerField'.")
        elif self.nome == 'CUSTOM':
            if self.tipo != 'CharField':
                raise ValidationError(f"Para o campo '{self.nome}', o tipo disponível é 'CharField'.")
        
        # Validações adicionais com base no tipo do campo
        if self.tipo == 'PhoneField':
            phone_field_value = getattr(self, 'valor', None)
            if phone_field_value:
                self.phone_regex(self.valor)
        elif self.tipo == 'DateOfBirth':
            date_value = getattr(self, 'valor', None)
            if date_value:
                min_date = timezone.datetime(1918, 1, 1).date()
                max_date = timezone.now().date()
                if date_value < min_date or date_value > max_date:
                    raise ValidationError('Data de nascimento inválida.')
        elif self.tipo == 'EmailField':
            email_value = getattr(self, 'valor', None)
            if email_value:
                self.email_validator(email_value)

    def get_nome_display(self):
        # Retorna o nome completo do campo, levando em consideração um nome personalizado para 'CUSTOM'
        if self.nome == 'CUSTOM' and self.custom_nome:
            return self.custom_nome
        return dict(self.NOMES).get(self.nome, '')

    def __str__(self):
        return self.get_nome_display()

    def __str__(self):
        return self.nome

class Proposta(models.Model):
    campos_dinamicos = models.ManyToManyField(CampoDinamico, through='ValorCampoDinamico')
    status = models.CharField(max_length=10, blank=True, null=True)
    def __str__(self):
        return f"Proposta {self.pk}"

class ValorCampoDinamico(models.Model):
    proposta = models.ForeignKey(Proposta, on_delete=models.CASCADE, related_name='valores_campo_dinamico')
    campo_dinamico = models.ForeignKey(CampoDinamico, on_delete=models.CASCADE)
    valor = models.CharField(max_length=255, blank=True, null=True)

    def get_valor(self):
        return self.valor
