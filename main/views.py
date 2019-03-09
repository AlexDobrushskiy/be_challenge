import json

from django.http import JsonResponse

from django.views import View

from main.loaders import PatientLoader, PaymentLoader


class PatientImportView(View):
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


class PaymentImportView(View):
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
