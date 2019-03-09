import json

from django.test import TestCase, Client

import random
import string
from main.loaders import PatientLoader, PATIENT_EXT_ID, PaymentLoader, PAYMENT_EXT_ID
from main.models import Patient, Payment


def generate_patient_json(number_of_records):
    result = []
    for i in range(number_of_records):
        record = {
            "firstName": ''.join(random.choices(string.ascii_letters, k=random.randint(3, 25))),
            "lastName": ''.join(random.choices(string.ascii_letters, k=random.randint(3, 25))),
            "dateOfBirth": "{}-{}-{}".format(random.randint(1900, 2100), random.randint(1, 12), random.randint(1, 28)),
            "externalId": ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        }
        result.append(record)
    return result


def generate_payment_json(number_of_records):
    result = []
    for i in range(number_of_records):
        record = {
            "amount": random.uniform(1., 100.),
            "patientId": ''.join(random.choices(string.ascii_letters + string.digits, k=64)),
            "externalId": ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        }
        result.append(record)
    return result


def generate_payment_for_patient(amount, patient_ext_id):
    return {
        "amount": amount,
        "patientId": patient_ext_id,
        "externalId": ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    }


class PatientLoaderTestCase(TestCase):
    def setUp(self):
        self.data = generate_patient_json(10)

    def test_basic_load(self):
        self.assertEqual(Patient.objects.count(), 0)
        loader = PatientLoader(self.data)
        loader.load()
        self.assertEqual(Patient.objects.count(), 10)

    def test_basic_large_load(self):
        data = generate_patient_json(10000)
        self.assertEqual(Patient.objects.count(), 0)
        loader = PatientLoader(data)
        loader.load()
        self.assertEqual(Patient.objects.count(), 10000)

    def test_change_first_name(self):
        data = generate_patient_json(10)
        loader = PatientLoader(data)
        loader.load()
        self.assertEqual(Patient.objects.count(), 10)
        ext_id = data[0][PATIENT_EXT_ID]
        data[0]['firstName'] = 'AAAAAAAAAAAAA'
        loader = PatientLoader(data)
        self.assertNotEqual(Patient.objects.get(external_id=ext_id).first_name, 'AAAAAAAAAAAAA')
        loader.load()
        self.assertEqual(Patient.objects.get(external_id=ext_id).first_name, 'AAAAAAAAAAAAA')

    def test_delete_some_patients(self):
        data = generate_patient_json(10)
        loader = PatientLoader(data)
        loader.load()
        self.assertEqual(Patient.objects.count(), 10)
        data = data[:5]
        loader = PatientLoader(data)
        loader.load()
        self.assertEqual(Patient.objects.count(), 5)


class PaymentLoaderTestCase(TestCase):
    def setUp(self):
        self.data = generate_payment_json(10)

    def test_basic_load(self):
        self.assertEqual(Payment.objects.count(), 0)
        loader = PaymentLoader(self.data)
        loader.load()
        self.assertEqual(Payment.objects.count(), 10)

    def test_basic_large_load(self):
        data = generate_payment_json(10000)
        self.assertEqual(Payment.objects.count(), 0)
        loader = PaymentLoader(data)
        loader.load()
        self.assertEqual(Payment.objects.count(), 10000)

    def test_change_amount(self):
        data = generate_payment_json(10)
        loader = PaymentLoader(data)
        loader.load()
        self.assertEqual(Payment.objects.count(), 10)
        ext_id = data[0][PAYMENT_EXT_ID]
        data[0]['amount'] = 0.99
        loader = PaymentLoader(data)
        self.assertNotEqual(Payment.objects.get(external_id=ext_id).amount, 0.99)
        loader.load()
        self.assertEqual(Payment.objects.get(external_id=ext_id).amount, 0.99)

    def test_delete_some_patients(self):
        data = generate_payment_json(10)
        loader = PaymentLoader(data)
        loader.load()
        self.assertEqual(Payment.objects.count(), 10)
        data = data[:5]
        loader = PaymentLoader(data)
        loader.load()
        self.assertEqual(Payment.objects.count(), 5)


class PatientViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_basic_import(self):
        data = generate_patient_json(10)
        self.assertEqual(Patient.objects.count(), 0)
        response = self.client.post('/patients/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Patient.objects.count(), 10)

    def test_fetching(self):
        data = generate_patient_json(10)
        loader = PatientLoader(data)
        loader.load()
        response = self.client.get('/patients/')
        data = json.loads(response.content)
        self.assertEqual(len(data), 10)

    def test_fetching_payment_min_filter(self):
        data = generate_patient_json(10)
        loader = PatientLoader(data)
        loader.load()
        payment_data = list()
        payment_data.append(generate_payment_for_patient(5, data[0]['externalId']))
        payment_data.append(generate_payment_for_patient(6, data[0]['externalId']))
        payment_data.append(generate_payment_for_patient(15, data[1]['externalId']))
        payment_data.append(generate_payment_for_patient(62, data[2]['externalId']))
        payment_loader = PaymentLoader(payment_data)
        payment_loader.load()
        response = self.client.get('/patients/?payment_min=10')
        data = json.loads(response.content)
        self.assertEqual(len(data), 3)

    def test_fetching_payment_max_filter(self):
        data = generate_patient_json(10)
        loader = PatientLoader(data)
        loader.load()
        payment_data = list()
        payment_data.append(generate_payment_for_patient(5, data[0]['externalId']))
        payment_data.append(generate_payment_for_patient(6, data[0]['externalId']))
        payment_data.append(generate_payment_for_patient(15, data[1]['externalId']))
        payment_data.append(generate_payment_for_patient(62, data[2]['externalId']))
        payment_loader = PaymentLoader(payment_data)
        payment_loader.load()
        response = self.client.get('/patients/?payment_max=12')
        data = json.loads(response.content)
        self.assertEqual(len(data), 8)

    def test_fetching_payment_min_max_filter(self):
        data = generate_patient_json(10)
        loader = PatientLoader(data)
        loader.load()
        payment_data = list()
        payment_data.append(generate_payment_for_patient(5, data[0]['externalId']))
        payment_data.append(generate_payment_for_patient(6, data[0]['externalId']))
        payment_data.append(generate_payment_for_patient(15, data[1]['externalId']))
        payment_data.append(generate_payment_for_patient(62, data[2]['externalId']))
        payment_data.append(generate_payment_for_patient(5, data[3]['externalId']))
        payment_loader = PaymentLoader(payment_data)
        payment_loader.load()
        response = self.client.get('/patients/?payment_max=16&payment_min=10')
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)


class PaymentViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_basic_import(self):
        data = generate_payment_json(10)
        self.assertEqual(Payment.objects.count(), 0)
        response = self.client.post('/payments/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.count(), 10)

    def test_fetching(self):
        data = generate_payment_json(10)
        loader = PaymentLoader(data)
        loader.load()
        response = self.client.get('/payments/')
        data = json.loads(response.content)
        self.assertEqual(len(data), 10)

    def test_fetching_with_filter(self):
        data = generate_payment_json(10)
        data[0]['patientId'] = '___SOME UNIQUE EXT ID HERE___'
        data[1]['patientId'] = '___SOME UNIQUE EXT ID HERE___'
        data[2]['patientId'] = '___SOME UNIQUE EXT ID HERE___'
        loader = PaymentLoader(data)
        loader.load()
        response = self.client.get('/payments/')
        data = json.loads(response.content)
        self.assertEqual(len(data), 10)

        response = self.client.get('/payments/?external_id=___SOME UNIQUE EXT ID HERE___')
        data = json.loads(response.content)
        self.assertEqual(len(data), 3)
