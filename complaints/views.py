from django.shortcuts import render
from django.http import HttpResponse, Http404
from complaints.models import Complaint, Department
from django.core.paginator import Paginator, InvalidPage
from complaints.models import Complaint, ClassifierOG, GroupTag
from django.http import HttpResponse
from django.template.loader import render_to_string
#from weasyprint import HTML
import tempfile

