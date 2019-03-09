import json

from django.http import JsonResponse

from django.views import View

from main.loaders import PatientLoader, PaymentLoader
from main.models import Payment

EXTERNAL_ID_QUERY_PARAM = 'external_id'


class PatientView(View):
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
