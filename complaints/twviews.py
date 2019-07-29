from django.views.generic.base import TemplateView
from complaints.models import Complaint, ClassifierOG#, GroupTag
from django.contrib.auth.models import User, Group
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import ContextMixin
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView, DayArchiveView
from django.shortcuts import redirect, render, render_to_response
from django.contrib import messages
from django.conf import settings
from complaints.templatetags.filters import ComplaintFilter, ComplaintFilterGroup
from complaints.forms import ComplaintForm
from django.core.mail import send_mail, BadHeaderError
from dal import autocomplete
import datetime
from calendar import monthrange

now = datetime.datetime.now()
'''
class GroupTagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return GroupTag.objects.none()
        qs = GroupTag.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs
'''
class GroupListMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super(GroupListMixin, self).get_context_data(**kwargs)
        context["groups"] = Group.objects.order_by("name")
        return context

class ClassifierOGAutocomp(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = ClassifierOG.objects.all()
        if self.q:
            qs = qs.filter(title__istartswith=self.q)
        return qs


def cap(request):
    return render(request, 'cap.html')

# ************************** АРХИВ ЖАЛОБ ******************************************************
class ComplaintArchiveView(ArchiveIndexView):
    model = Complaint
    date_field = "reg_date"
    template_name = "arhives/archive.html"
    paginate_by = 25

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

class ComplaintYearArchiveView(YearArchiveView):
    model = Complaint
    date_field = "reg_date"
    template_name = "arhives/year_archive.html"
    paginate_by = 25
    make_object_list = True

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

class ComplaintMonthArchiveView(MonthArchiveView):
    model = Complaint
    date_field = "reg_date"
    template_name = "arhives/month_archive.html"
    paginate_by = 25
    make_object_list = True
    month_format = "%m"

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

class ComplaintDayArchiveView(DayArchiveView):
    model = Complaint
    date_field = "reg_date"
    template_name = "arhives/day_archive.html"
    paginate_by = 25
    make_object_list = True
    month_format = "%m"

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)
# ************************** ОТОБРАЖЕНИЕ ЖАЛОБ ******************************************************
# Показать все жалобы в текущем отделе
class ComplaintListView(ListView, GroupListMixin):
    template_name = "index.html"
    paginate_by = 25
    group = None
    date_field = "reg_date"

    def get(self, request, *args, **kwargs):
        #self.paginate_by = self.request.session.get('num', 10)
        if self.kwargs["group_id"] == None:
            #self.group = Group.objects.first()
            user = request.user
            groups = [g.id for g in user.groups.all()]
            self.group = Group.objects.get(pk=groups[0])
        else:
            self.group = Group.objects.get(pk=self.kwargs["group_id"])
        users = User.objects.filter(groups=self.group)
        if request.user in users:
            return super(ComplaintListView, self).get(request, *args, **kwargs)
        else:
            return redirect("cap")

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super(ComplaintListView, self).get_context_data(**kwargs)

        context["group"] = self.group
        return context

    def get_queryset(self):
        start_date = datetime.date(now.year, 1, 1)
        end_date = datetime.date(now.year, 12, monthrange(now.year, 12)[1])
        return Complaint.objects.filter(group=self.group, reg_date__range=(start_date, end_date)).order_by("reg_date")

# Показать выбранную жалобу
class ComplaintDetailView(DetailView, GroupListMixin):
    template_name = "complaint.html"
    model = Complaint
    pk_url_kwarg = "complaint_id"
    def get_context_data(self, **kwargs):
        context = super(ComplaintDetailView, self).get_context_data(**kwargs)
        try:
            context["pn"] = self.request.GET["page"]
        except KeyError:
            context["pn"] = "1"
        return context


# ************************** ДОБАВЛЕНИЕ ЖАЛОБ ******************************************************
class ComplaintCreate(TemplateView):
    form = None
    template_name = "complaint_add.html"

    def get(self, request, *args, **kwargs):
        self.form = ComplaintForm()
        return super(ComplaintCreate, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ComplaintCreate, self).get_context_data(**kwargs)
        context["form"] = self.form
        return context

    def post(self, request, *args, **kwargs):
        self.form = ComplaintForm(request.POST, request.FILES)
        if self.form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Жалоба успешно добавлена!")
            obj = self.form.save(commit=False)
            users = User.objects.filter(groups=obj.group)
            emails = []
            for user in users:
                emails.append(user.email)
            if not emails:
                emails.append('admin@uszn.avo.ru')
            send_mail('НОВАЯ ЖАЛОБА ОТ : {}'.format(obj.fio),
                      'Номер жалобы: {} \nФИО: {}\nСодержание обращения: {} \nСсылка: https://192.168.10.21/complaints/'.format(obj.name, obj.fio, obj.description), settings.EMAIL_HOST_USER, emails, fail_silently=False)
            self.form.save()
            return redirect("index")
        else:
            messages.add_message(request, messages.ERROR, "Ошибка добавления! {}".format(self.form.errors))
            return super(ComplaintCreate, self).get(request, *args, **kwargs)

# ************************** РЕДАКТИРОВАНИЕ ЖАЛОБ ******************************************************
class ComplaintUpdate(TemplateView):
    form = None
    template_name = "complaint_edit.html"
    def get(self, request, *args, **kwargs):
        self.form = ComplaintForm(instance=Complaint.objects.get(pk=self.kwargs["complaint_id"]))
        return super(ComplaintUpdate, self).get(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super(ComplaintUpdate, self).get_context_data(**kwargs)
        context["complaint"] = Complaint.objects.get(pk=self.kwargs["complaint_id"])
        context["form"] = self.form
        return context
    def post(self, request, *args, **kwargs):
        complaint = Complaint.objects.get(pk=self.kwargs["complaint_id"])
        self.form = ComplaintForm(request.POST, request.FILES, instance=complaint)
        print(self.form.errors)
        if self.form.is_valid():
            self.form.save()
            messages.add_message(request, messages.SUCCESS, "Жалоба успешно обновлена!")
            return redirect("index", group_id=complaint.group.id)
        else:
            messages.add_message(request, messages.ERROR, "Ошибка обновления! {}".format(self.form.errors))
            return super(ComplaintUpdate, self).get(request, *args, **kwargs)


# ************************** УДАЛЕНИЕ ЖАЛОБ ******************************************************
class ComplaintDelete(TemplateView):
    pass
