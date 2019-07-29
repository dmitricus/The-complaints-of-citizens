from django import forms
from dal import autocomplete
import datetime
from calendar import monthrange
#from bootstrap_datepicker.widgets import DatePicker
from complaints.models import Complaint, ClassifierOG#, GroupTag

now = datetime.datetime.now()
start_date_year = datetime.date(now.year, now.month, 1)
end_date_year = datetime.date(now.year, now.month, monthrange(now.year, now.month)[1])

class ComplaintForm(autocomplete.FutureModelForm):
    classifier_og = forms.ModelChoiceField(
        queryset=ClassifierOG.objects.all(),
        widget=autocomplete.ModelSelect2(url='classifier-autocomplete'),
        label="Классификатор ОГ:"
    )
    '''group_tag = forms.ModelChoiceField(
        queryset=GroupTag.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='grouptag-autocomplete'),
        label="Копия:"
    )
    '''
    class Meta:
        model = Complaint
        # fields = ('__all__')
        fields = ['name', 'fio', 'address', 'res_date', 'description', 'admissions',
                  'in_stock', 'group', 'classifier_og', 'file_complaint', 'file_answer',
                  'collective_appeal', 'repeated_appeal', 'control_appeal',
                  'appeal_is_considered', 'theme_issues']

        widgets = {
            'res_date': forms.DateInput(format=('%Y-%m-%d'),
                                        attrs={'type': 'date', 'class': 'form-control'}),
        }


class StatGenerateForm(forms.Form):
    start_date = forms.DateField(label='Начало отчетного периода', widget=forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date', 'class': 'form-control datepicker'}))
    end_date = forms.DateField(label='Конец отчетного периода', widget=forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date', 'class': 'form-control datepicker'}))

    class Meta:
        fields = ['start_date', 'end_date']

