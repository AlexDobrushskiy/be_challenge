from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Patient(BaseModel):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    middle_name = models.CharField(max_length=256, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    external_id = models.CharField(max_length=256, unique=True)


class Payment(BaseModel):
    amount = models.FloatField()
    patient_external_id = models.CharField(max_length=256)
    external_id = models.CharField(max_length=256, unique=True)
