from django.conf.urls import url
from complaints.charts import ChartVsiew, get_data, ChartData, ComplaintStatisticChartData

import complaints.twviews as complaints
from .logic import ReportGenerator, statistic, generate_document, search, search_group
from complaints.models import Complaint, Department
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^(?:(?P<group_id>\d+)/)?$', login_required(complaints.ComplaintListView.as_view()), name="index"),
    url(r'^complaint/(?P<complaint_id>\d+)/$', login_required(complaints.ComplaintDetailView.as_view()), name="complaint"),
    url(r'^complaint/add/$', permission_required("complaints.can_administrator", login_url='cap')(complaints.ComplaintCreate.as_view()), name="complaint_add"),
    url(r'^complaint/(?P<complaint_id>\d+)/edit/$', login_required(complaints.ComplaintUpdate.as_view()), name="complaint_edit"),
    url(r'^complaint/(?P<complaint_id>\d+)/delete/$', permission_required("complaints.can_administrator", login_url='cap')(complaints.ComplaintDelete.as_view()), name="complaint_delete"),
    url(r'^archive/$', permission_required("complaints.can_administrator", login_url='cap')(complaints.ComplaintArchiveView.as_view()), name="archive"),
    url(r'^archive/(?P<year>\d{4})/$', permission_required("complaints.can_administrator", login_url='cap')(complaints.ComplaintYearArchiveView.as_view()), name="year_archive"),
    url(r'^archive/(?P<year>\d{4})/(?P<month>\d+)/$', permission_required("complaint.can_administrator", login_url='cap')(complaints.ComplaintMonthArchiveView.as_view()), name="month_archive"),
    url(r'^archive/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', permission_required("complaint.can_administrator", login_url='cap')(complaints.ComplaintDayArchiveView.as_view()), name="day_archive"),
    url(r'^login/', LoginView.as_view(template_name="login.html", extra_context = {"groups": Group.objects.all()}), name="login",),
    url(r'^logout/', LogoutView.as_view(template_name="logout.html", extra_context = {"groups": Group.objects.all()}), name="logout"),
    url(r'^search/$', permission_required("complaints.can_administrator", login_url='cap')(search), name='search'),
    url(r'^search-group/$', permission_required("complaints.can_customers", login_url='cap')(search_group), name='search-group'),
    url(r'^classifier-autocomplete/$', complaints.ClassifierOGAutocomp.as_view(), name='classifier-autocomplete'),
    #url(r'^grouptag-autocomplete/$', GroupTagAutocomplete.as_view(), name='grouptag-autocomplete'),
    url(r'^cap/$', complaints.cap, name="cap"),
    url(r'^statistic/$', permission_required("complaints.can_administrator", login_url='cap')(statistic), name="statistic"),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),
    url(r'^generate/document/$', generate_document, name='generate_document'),
    url(r'^statistic/charts/$', ChartVsiew.as_view(), name='chart-bar'),
    url(r'^statistic/api/data/$', get_data, name='api-data'),
    url(r'^statistic/api/chart/data/$', ChartData.as_view()),
    url(r'^statistic/api/complaintchart/data/$', ComplaintStatisticChartData.as_view()),
]
