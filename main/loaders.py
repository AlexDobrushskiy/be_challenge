from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError

from main.models import Patient, Payment

PATIENT_MANDATORY_FIELDS = ['firstName', 'lastName', 'externalId']
PATIENT_EDITABLE_FIELDS_MAPPING = {'firstName': 'first_name', 'lastName': 'last_name', 'dateOfBirth': 'date_of_birth'}
PATIENT_EXT_ID = 'externalId'

PAYMENT_MANDATORY_FIELDS = ['amount', 'patientId', 'externalId']
PAYMENT_EDITABLE_FIELDS_MAPPING = {'amount': 'amount', 'patientId': 'patient_external_id'}
PAYMENT_EXT_ID = 'externalId'


def patient_valid(patient):
    for field in PATIENT_MANDATORY_FIELDS:
        if field not in patient:
            return False
    if not patient[PATIENT_EXT_ID]:
        return False
    return True


def payment_valid(payment):
    for field in PAYMENT_MANDATORY_FIELDS:
        if field not in payment:
            return False
    if not payment[PAYMENT_EXT_ID]:
        return False
    return True


class PatientLoader:
    def __init__(self, data):
        self.data = data

    def load(self):
        Patient.objects.all().delete()
        objects = []
        for patient in self.data:
            if not patient_valid(patient):
                continue
            obj = Patient(external_id=patient[PATIENT_EXT_ID])
            for ext_name, int_name in PATIENT_EDITABLE_FIELDS_MAPPING.items():
                if ext_name in patient:
                    setattr(obj, int_name, patient[ext_name])
            objects.append(obj)
        Patient.objects.bulk_create(objects)


class PaymentLoader:
    def __init__(self, data):
        self.data = data

    def load(self):
        Payment.objects.all().delete()
        objects = []
        for payment in self.data:
            if not payment_valid(payment):
                continue
            obj = Patient(external_id=payment[PAYMENT_EXT_ID])
            for ext_name, int_name in PAYMENT_EDITABLE_FIELDS_MAPPING.items():
                if ext_name in payment:
                    setattr(obj, int_name, payment[ext_name])
            objects.append(obj)
        Payment.objects.bulk_create(objects)
