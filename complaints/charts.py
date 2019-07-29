from django.contrib.auth import get_user_model
from complaints.models import Complaint
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
import datetime
from calendar import monthrange

from rest_framework.views import APIView
from rest_framework.response import Response

now = datetime.datetime.now()


User = get_user_model()

class ChartVsiew(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'statistic/charts.html', {})


def get_data(request, *args, **kwargs):
    data = {
        "sales": 100,
        "customers": 10,
    }
    return JsonResponse(data)


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        qs_count = User.objects.all().count()
        label = 'Электронные обращения'
        labels = ["Квартал I", "Квартал II", "Квартал III", "Квартал IV"]
        default_items = [qs_count, 20, 24, 25]
        data = {
            "label": label,
            "labels": labels,
            "default": default_items,
        }
        return Response(data)

class ComplaintStatisticChartData(APIView):
    def get(self, request, format=None):
        start_date = datetime.date(now.year, 1, 1)
        end_date = datetime.date(now.year, 12, monthrange(now.year, 12)[1])
        kv1_start_date = datetime.date(now.year, 1, 1)
        kv1_end_date = datetime.date(now.year, 3, monthrange(now.year, 3)[1])
        kv2_start_date = datetime.date(now.year, 4, 1)
        kv2_end_date = datetime.date(now.year, 6, monthrange(now.year, 6)[1])
        kv3_start_date = datetime.date(now.year, 7, 1)
        kv3_end_date = datetime.date(now.year, 9, monthrange(now.year, 9)[1])
        kv4_start_date = datetime.date(now.year, 10, 1)
        kv4_end_date = datetime.date(now.year, 12, monthrange(now.year, 12)[1])

        #year_type_len = Complaint.objects.filter(in_stock_id=1, reg_date__range=(start_date, end_date)).count()
        kv1_type_len = Complaint.objects.filter(in_stock_id=1, reg_date__range=(kv1_start_date, kv1_end_date)).count()
        kv2_type_len = Complaint.objects.filter(in_stock_id=1, reg_date__range=(kv2_start_date, kv2_end_date)).count()
        kv3_type_len = Complaint.objects.filter(in_stock_id=1, reg_date__range=(kv3_start_date, kv3_end_date)).count()
        kv4_type_len = Complaint.objects.filter(in_stock_id=1, reg_date__range=(kv4_start_date, kv4_end_date)).count()

        label = 'Электронные обращения'
        labels = ["Квартал I", "Квартал II", "Квартал III", "Квартал IV"]
        default_items = [kv1_type_len, kv2_type_len, kv3_type_len, kv4_type_len]
        data = {
            "label": label,
            "labels": labels,
            "default": default_items,
        }
        return Response(data)