from django.contrib.auth.models import User, Group
import django_filters
from django import forms

from dal import autocomplete
from complaints.models import Complaint, ClassifierOG

class ComplaintFilter(django_filters.FilterSet):
    classifier_og = django_filters.ModelChoiceFilter(
        queryset=ClassifierOG.objects.all(),
        widget=autocomplete.ModelSelect2(url='classifier-autocomplete'),
        label="Классификатор ОГ:"
    )
    name = django_filters.CharFilter(label="Номер обращения:")
    res_date = django_filters.DateFilter(label="Дата ответа:", widget=forms.TextInput(attrs={'type': 'date'}))  # Дата ответа автору
    reg_date = django_filters.DateFilter(label="Дата регистрации:", widget=forms.TextInput(attrs={'type': 'date'}))  # Дата ответа автору


    class Meta:
        model = Complaint
        fields = ['name', 'fio', 'admissions', 'classifier_og', 'group', 'address', 'reg_date', 'res_date', 'in_stock']
        widgets = {
            'reg_date': forms.DateInput(format=('%Y-%m-%d'),
                                        attrs={'type': 'date', 'class': 'form-control datepicker'}),
            'res_date': forms.DateInput(format=('%Y-%m-%d'),
                                        attrs={'type': 'date', 'class': 'form-control datepicker'}),
        }

class ComplaintFilterGroup(django_filters.FilterSet):
    classifier_og = django_filters.ModelChoiceFilter(
        queryset=ClassifierOG.objects.all(),
        widget=autocomplete.ModelSelect2(url='classifier-autocomplete'),
        label="Классификатор ОГ:"
    )
    name = django_filters.CharFilter(label="Номер обращения:")
    res_date = django_filters.DateFilter(label="Дата ответа:", widget=forms.TextInput(attrs={'type': 'date'}))  # Дата ответа автору
    reg_date = django_filters.DateFilter(label="Дата регистрации:", widget=forms.TextInput(attrs={'type': 'date'}))  # Дата ответа автору


    class Meta:
        model = Complaint
        fields = ['name', 'fio', 'admissions', 'classifier_og', 'address', 'reg_date', 'res_date', 'in_stock']
        widgets = {
            'reg_date': forms.DateInput(format=('%Y-%m-%d'),
                                        attrs={'type': 'date', 'class': 'form-control datepicker'}),
            'res_date': forms.DateInput(format=('%Y-%m-%d'),
                                        attrs={'type': 'date', 'class': 'form-control datepicker'}),
        }