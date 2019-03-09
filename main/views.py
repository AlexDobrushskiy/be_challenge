import json

from django.http import JsonResponse

from django.views import View
from django.db import connection

from main.loaders import PatientLoader, PaymentLoader
from main.models import Payment, Patient

EXTERNAL_ID_QUERY_PARAM = 'external_id'


def get_patient_filtered_query(payment_min=None, payment_max=None):
    query = '''
            SELECT 
                p1.first_name, 
                p1.last_name, 
                p1.middle_name, 
                p1.date_of_birth, 
                p1.external_id, 
            COALESCE(sum(p2.amount), 0) as total_amount 
            FROM main_patient p1 
            LEFT JOIN main_payment p2 
            ON p1.external_id=p2.patient_external_id 
            GROUP BY p1.external_id        
            '''
    if payment_min or payment_max:
        if payment_min and payment_max:
            query = '''
            select * from ({}) t1 where t1.total_amount>={} and t1.total_amount<={}
            '''.format(query, payment_min, payment_max)
        else:
            if payment_min:
                query = '''
                select * from ({}) t1 where t1.total_amount>={}
                '''.format(query, payment_min)
            else:
                query = '''
                select * from ({}) t1 where t1.total_amount<={}
                '''.format(query, payment_max)
    return query


def get_patient_data(payment_min=None, payment_max=None):
    query = get_patient_filtered_query(payment_min, payment_max)
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    result = []
    for row in rows:
        record = {
            "firstName": row[0],
            "lastName": row[1],
            "middleName": row[2],
            "dateOfBirth": row[3],
            "externalId": row[4]
        }
        result.append(record)
    return result


class PatientView(View):
    def get(self, request):
        data = get_patient_data(request.GET.get('payment_min'), request.GET.get('payment_max'))
        return JsonResponse(data, status=200, safe=False)

    def post(self, request):
        data = request.body
        try:
            json_data = json.loads(data)
            loader = PatientLoader(json_data)
            # in production I'd rather use async queue for this task
            # as this is potentially long task - it is not the best idea
            # to process it before response
            loader.load()
        except Exception as ex:
            return JsonResponse({'error': '{}'.format(ex)}, status=400)
        return JsonResponse({'status': 'Data is processed'}, status=200)


class PaymentView(View):
    def get(self, request):
        # In production case pagination would be absolutely required here.
        qs = Payment.objects.all()
        if EXTERNAL_ID_QUERY_PARAM in request.GET:
            external_id = request.GET.get(EXTERNAL_ID_QUERY_PARAM)
            qs = Payment.objects.filter(patient_external_id=external_id)
        result = []
        for payment in qs:
            record = {
                "amount": payment.amount,
                "patientId": payment.patient_external_id,
                "externalId": payment.external_id
            }
            result.append(record)
        return JsonResponse(result, status=200, safe=False)

    def post(self, request):
        data = request.body
        try:
            json_data = json.loads(data)
            loader = PaymentLoader(json_data)
            # in production I'd rather use async queue for this task
            # as this is potentially long task - it is not the best idea
            # to process it before response
            loader.load()
        except Exception as ex:
            return JsonResponse({'error': '{}'.format(ex)}, status=400)
        return JsonResponse({'status': 'Data is processed'}, status=200)
