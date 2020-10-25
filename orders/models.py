from django.db import models
from django.core.validators import RegexValidator


class Correios(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # https://www.correios.com.br/enviar-e-receber/correspondencia/precisa-de-ajuda/guia-tecnico-de-enderecamento-de-correspondencias
    code = models.CharField(
        max_length=13,
        validators=[RegexValidator(regex=r'^\w{2}\d{9}\w{2}$')]
    )
    name = models.CharField(max_length=100)
    delivered = models.BooleanField(default=False)
    last_update = models.DateTimeField(null=True)
    cpf_registered = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['created']),
            models.Index(fields=['updated']),
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['delivered']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['code'],
                name='delivery',
                condition=models.Q(delivered=False)
            )
        ]


class CorreiosInfo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    order = models.ForeignKey('Correios', on_delete=models.CASCADE)
    date = models.DateTimeField()
    place = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    info = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'date', 'place', 'status'],
                name='status'
            ),
        ]
