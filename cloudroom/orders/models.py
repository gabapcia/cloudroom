from django.db import models


class Correios(models.Model):
    code            = models.CharField(max_length=13, db_index=True)
    delivered       = models.BooleanField(default=False, db_index=True)
    last_update     = models.DateTimeField(null=True, blank=True)
    cpf_registered  = models.BooleanField(default=False)


class CorreiosInfo(models.Model):
    order   = models.ForeignKey('Correios', on_delete=models.CASCADE)
    date    = models.DateTimeField()
    place   = models.CharField(max_length=100)
    status  = models.CharField(max_length=100)
    info    = models.TextField()

