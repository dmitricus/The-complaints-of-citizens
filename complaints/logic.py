from secretary import Renderer
from django.http import HttpResponse
import os, sys, tempfile, shutil
from calendar import monthrange
import locale
import sys
import datetime
from django.contrib.auth.models import User, Group
from complaints.templatetags.filters import ComplaintFilter, ComplaintFilterGroup
from complaints.models import Complaint
from django.shortcuts import redirect, render, render_to_response
from complaints.forms import StatGenerateForm

if sys.platform == 'win32':
    locale.setlocale(locale.LC_ALL, 'rus_rus')
else:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

now = datetime.datetime.now()
start_date_year = datetime.date(now.year, 1, 1)
end_date_year = datetime.date(now.year, 12, monthrange(now.year, 12)[1])

class ReportGenerator():
    """ Class ReportGenerator """

    @staticmethod
    def create_report(data):
        engine = Renderer()
        root = os.path.dirname(__file__)
        document = root + '/templates/bedjango/template.odt'
        DIRECTORY = root + '/templates/bedjango/tmp/'
        result = engine.render(document, data=data)
        tempfile.tempdir = DIRECTORY
        response = HttpResponse(content_type='application/vnd.oasis.opendocument.text; charset=UTF-8')
        response['Content-Disposition'] = 'inline; filename=report_on_complaint_{}.odt'.format(now.strftime('%d%m%Y'))

        with tempfile.NamedTemporaryFile(delete=False) as output:
            output.write(result)
            output.flush()
            output = open(output.name, 'rb')
            response.write(output.read())
        clear_folder(DIRECTORY)
        return response


# Очистка временных файлов
def clear_folder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            else:
                shutil.rmtree(file_path)
            print("[Deleted] ", file_path)
        except:
            print(str(sys.exc_info()[1]))


# Экспорт татистики в odt
def getComplaintRangeDate(start_date, end_date):
    complaint_set = Complaint.objects.filter(admissions=2, in_stock_id=1,
                                             reg_date__range=(start_date, end_date)).count()
    return complaint_set


# Универсальная функция генерации данных для отчета
def get_render_stat(admissions, date_stat, start_date, end_date, old_start_date, old_end_date):
    # Электронные обращения
    stat_type = Complaint.objects.filter(admissions=admissions, in_stock_id=1,
                                         reg_date__range=(start_date, end_date)).count()
    # Обращений за отчетный период
    stat_complaint = Complaint.objects.filter(admissions=admissions, reg_date__range=(start_date, end_date)).count()
    # Коллективные обращения
    collective_appeal = Complaint.objects.filter(admissions=admissions, collective_appeal=True,
                                                 reg_date__range=(start_date, end_date)).count()
    # Повторные обращения
    repeated_appeal = Complaint.objects.filter(admissions=admissions, repeated_appeal=True,
                                               reg_date__range=(start_date, end_date)).count()

    # Количество обращений, перешедших с предыдущего периода
    stat_old_complaint_cost = Complaint.objects.filter(admissions=admissions, appeal_is_considered=False,
                                                       reg_date__range=(
                                                           old_start_date, old_end_date)).count()

    # Поступило за отчетный период
    stat_complaint_cost = Complaint.objects.filter(admissions=admissions, reg_date__range=(
        start_date, end_date)).count()

    # Поступило всего отчетный период + предыдущий период
    all_cost = stat_old_complaint_cost + stat_complaint_cost

    ######################################### Тематика вопросов ########################################################
    # основы государственного управления
    stat_public_admin_cost = Complaint.objects.filter(admissions=admissions, theme_issues=1,
                                                      reg_date__range=(start_date, end_date)).count()
    # социальная защита населения
    stat_social_protection_cost = Complaint.objects.filter(admissions=admissions, theme_issues=2,
                                                           reg_date__range=(start_date, end_date)).count()
    # улучшение жилищных условий
    stat_housing_conditions_cost = Complaint.objects.filter(admissions=admissions, theme_issues=3,
                                                            reg_date__range=(start_date, end_date)).count()
    # образование
    stat_education_cost = Complaint.objects.filter(admissions=admissions, theme_issues=4,
                                                   reg_date__range=(start_date, end_date)).count()
    # здравоохранение
    stat_health_cost = Complaint.objects.filter(admissions=admissions, theme_issues=5,
                                                reg_date__range=(start_date, end_date)).count()
    # ЖКХ
    stat_hcs_cost = Complaint.objects.filter(admissions=admissions, theme_issues=6,
                                             reg_date__range=(start_date, end_date)).count()
    # законность и правопорядок
    stat_law_and_order_cost = Complaint.objects.filter(admissions=admissions, theme_issues=7,
                                                       reg_date__range=(start_date, end_date)).count()
    # иные
    stat_other_cost = Complaint.objects.filter(admissions=admissions, theme_issues=8,
                                               reg_date__range=(start_date, end_date)).count()
    data_content = {
        'date_stat': date_stat,
        'stat_complaint': stat_complaint,
        'stat_type': stat_type,
        'collective_appeal': collective_appeal,
        'repeated_appeal': repeated_appeal,
        'stat_old_complaint_cost': stat_old_complaint_cost,
        'stat_complaint_cost': stat_complaint_cost,
        'all_cost': all_cost,
        'stat_public_admin_cost': stat_public_admin_cost,
        'stat_social_protection_cost': stat_social_protection_cost,
        'stat_housing_conditions_cost': stat_housing_conditions_cost,
        'stat_education_cost': stat_education_cost,
        'stat_health_cost': stat_health_cost,
        'stat_hcs_cost': stat_hcs_cost,
        'stat_law_and_order_cost': stat_law_and_order_cost,
        'stat_other_cost': stat_other_cost,
    }

    return data_content


# Универсальная функция генерации аналогичных данных для отчетчетному периоду прошлого года
def get_render_old_stat(admissions, start_date, end_date, old_start_date, old_end_date):
    # Электронные обращения
    stat_type = Complaint.objects.filter(admissions=admissions, in_stock_id=1,
                                         reg_date__range=(start_date, end_date)).count()
    # Обращений за отчетный период
    stat_complaint = Complaint.objects.filter(admissions=admissions, reg_date__range=(start_date, end_date)).count()
    # Коллективные обращения
    collective_appeal = Complaint.objects.filter(admissions=admissions, collective_appeal=True,
                                                 reg_date__range=(start_date, end_date)).count()
    # Повторные обращения
    repeated_appeal = Complaint.objects.filter(admissions=admissions, repeated_appeal=True,
                                               reg_date__range=(start_date, end_date)).count()

    # Количество обращений, перешедших с предыдущего периода
    stat_old_complaint_cost = Complaint.objects.filter(admissions=admissions, appeal_is_considered=False,
                                                       reg_date__range=(
                                                           old_start_date, old_end_date)).count()

    # Поступило за отчетный период
    stat_complaint_cost = Complaint.objects.filter(admissions=admissions, reg_date__range=(
        start_date, end_date)).count()

    # Поступило всего отчетный период + предыдущий период
    all_cost = stat_old_complaint_cost + stat_complaint_cost

    ######################################### Тематика вопросов ########################################################
    # основы государственного управления
    stat_public_admin_cost = Complaint.objects.filter(admissions=admissions, theme_issues=1,
                                                      reg_date__range=(start_date, end_date)).count()
    # социальная защита населения
    stat_social_protection_cost = Complaint.objects.filter(admissions=admissions, theme_issues=2,
                                                           reg_date__range=(start_date, end_date)).count()
    # улучшение жилищных условий
    stat_housing_conditions_cost = Complaint.objects.filter(admissions=admissions, theme_issues=3,
                                                            reg_date__range=(start_date, end_date)).count()
    # образование
    stat_education_cost = Complaint.objects.filter(admissions=admissions, theme_issues=4,
                                                   reg_date__range=(start_date, end_date)).count()
    # здравоохранение
    stat_health_cost = Complaint.objects.filter(admissions=admissions, theme_issues=5,
                                                reg_date__range=(start_date, end_date)).count()
    # ЖКХ
    stat_hcs_cost = Complaint.objects.filter(admissions=admissions, theme_issues=6,
                                             reg_date__range=(start_date, end_date)).count()
    # законность и правопорядок
    stat_law_and_order_cost = Complaint.objects.filter(admissions=admissions, theme_issues=7,
                                                       reg_date__range=(start_date, end_date)).count()
    # иные
    stat_other_cost = Complaint.objects.filter(admissions=admissions, theme_issues=8,
                                               reg_date__range=(start_date, end_date)).count()
    old_data_content = {
        'stat_complaint': stat_complaint,
        'stat_type': stat_type,
        'collective_appeal': collective_appeal,
        'repeated_appeal': repeated_appeal,
        'stat_old_complaint_cost': stat_old_complaint_cost,
        'stat_complaint_cost': stat_complaint_cost,
        'all_cost': all_cost,
        'stat_public_admin_cost': stat_public_admin_cost,
        'stat_social_protection_cost': stat_social_protection_cost,
        'stat_housing_conditions_cost': stat_housing_conditions_cost,
        'stat_education_cost': stat_education_cost,
        'stat_health_cost': stat_health_cost,
        'stat_hcs_cost': stat_hcs_cost,
        'stat_law_and_order_cost': stat_law_and_order_cost,
        'stat_other_cost': stat_other_cost,
    }

    return old_data_content


def date_scatistic(start_date, end_date):
    # Текущий год
    start_date_year = datetime.date(start_date.year, 1, 1)
    end_date_year = datetime.date(end_date.year, 12, monthrange(end_date.year, 12)[1])
    # Квартал текущего года
    kv1_start_date = datetime.date(start_date.year, 1, 1)
    kv1_end_date = datetime.date(end_date.year, 3, monthrange(end_date.year, 3)[1])
    kv2_start_date = datetime.date(start_date.year, 4, 1)
    kv2_end_date = datetime.date(end_date.year, 6, monthrange(end_date.year, 6)[1])
    kv3_start_date = datetime.date(start_date.year, 7, 1)
    kv3_end_date = datetime.date(end_date.year, 9, monthrange(end_date.year, 9)[1])
    kv4_start_date = datetime.date(start_date.year, 10, 1)
    kv4_end_date = datetime.date(end_date.year, 12, monthrange(end_date.year, 12)[1])

    # Отчетный период
    #reporting_period_start = datetime.date(start_date.year, start_date.month, 1)
    #reporting_period_end = datetime.date(end_date.year, end_date.month, monthrange(end_date.year, end_date.month)[1])

    # Предыдущий отчетный период
    #old_reporting_period_start = datetime.date(start_date.year, (start_date.month - 1 or 12), 1)
    #old_reporting_period_end = datetime.date(end_date.year, (end_date.month - 1 or 12), monthrange(end_date.year, (end_date.month - 1 or 12))[1])

    # Отчетный период
    reporting_period_start = datetime.date(start_date.year, start_date.month, start_date.day)
    reporting_period_end = datetime.date(end_date.year, end_date.month, end_date.day)

    dayd = (monthrange((end_date.year - 1), (end_date.month - 1 or 12))[1]) - start_date.day

    # Предыдущий отчетный период
    old_reporting_period_start = datetime.date(start_date.year, (start_date.month - 1 or 12), start_date.day)
    old_reporting_period_end = datetime.date(end_date.year, (end_date.month - 1 or 12), monthrange(end_date.year, (end_date.month - 1 or 12))[1])

    return reporting_period_start, reporting_period_start, reporting_period_end, old_reporting_period_start, old_reporting_period_end


def old_date_scatistic(start_date, end_date):

    # Аналогичный отчетный период за прошлый год
    old_year_reporting_period_start = datetime.date((start_date.year - 1), start_date.month, start_date.day)
    old_year_reporting_period_end = datetime.date((end_date.year - 1), end_date.month, end_date.day)

    dayd = (monthrange((end_date.year - 1), (end_date.month - 1 or 12))[1]) - start_date.day

    # Аналогичный предыдущий отчетный период за прошлый год
    old_year_old_reporting_period_start = datetime.date((start_date.year - 1), (start_date.month - 1 or 12), start_date.day)
    old_year_old_reporting_period_end = datetime.date((end_date.year - 1), (end_date.month - 1 or 12), monthrange(end_date.year, (end_date.month - 1 or 12))[1])


    return old_year_reporting_period_start, old_year_reporting_period_end, old_year_old_reporting_period_start, old_year_old_reporting_period_end


def generate_document(request, admissions=2):
    complaint_list = Complaint.objects.all()
    data_content = None
    old_data_content = None
    if request.method == 'POST':
        form = StatGenerateForm(request.POST)
        if form.is_valid():
            # Получим данные с формы
            date, start_date, end_date, old_start_date, old_end_date = date_scatistic(form.cleaned_data['start_date'],
                                                                                      form.cleaned_data['end_date'])
            old_start_date, old_end_date, old_old_start_date, old_old_end_date = old_date_scatistic(
                form.cleaned_data['start_date'], form.cleaned_data['end_date'])
            # Передадим данные в функции расчета
            data_content = get_render_stat(admissions, date.strftime("%B %Y"), start_date, end_date, old_start_date,
                                           old_end_date)
            old_data_content = get_render_old_stat(admissions, old_start_date, old_end_date, old_old_start_date,
                                                   old_old_end_date)

    content = {
        'complaint_list': complaint_list.iterator(),
        'data_content': data_content,
        'old_data_content': old_data_content,
    }
    return ReportGenerator().create_report(content)


# показать текущую статистику по жалобам
def statistic(request):
    complaint_list = Complaint.objects.filter(reg_date__range=(start_date_year, end_date_year))
    form = StatGenerateForm()

    content = {
        'complaint_list': complaint_list,
        'form': form,
    }

    return render(request, 'statistic/statistic.html', content)


# поиск и фильтрация по всем жалобам
def search(request, paginate_by=25):
    complaint_list = Complaint.objects.all()
    complaint_filter = ComplaintFilter(request.GET, queryset=complaint_list)
    content = {
        'filter': complaint_filter,
        'paginate_by': paginate_by,
    }
    return render(request, 'search/search.html', content)


# поиск и фильтрация по группам
def search_group(request, paginate_by=25):
    user = request.user
    groups = [g.id for g in user.groups.all()]
    group = Group.objects.get(pk=groups[0])
    complaint_list = Complaint.objects.filter(group=group)
    complaint_filter = ComplaintFilterGroup(request.GET, queryset=complaint_list)
    content = {
        'filter': complaint_filter,
        'paginate_by': paginate_by,
    }
    return render(request, 'search/search-group.html', content)
