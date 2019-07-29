from django.db import models
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User, Group
from pytils import translit
import datetime

from calendar import monthrange
# Create your models here.

now = datetime.datetime.now()

# Текущий год
start_date = datetime.date(now.year, 1, 1)
end_date = datetime.date(now.year, 12, monthrange(now.year, 12)[1])
# Квартал текущего года
kv1_start_date = datetime.date(now.year, 1, 1)
kv1_end_date = datetime.date(now.year, 3, monthrange(now.year, 3)[1])
kv2_start_date = datetime.date(now.year, 4, 1)
kv2_end_date = datetime.date(now.year, 6, monthrange(now.year, 6)[1])
kv3_start_date = datetime.date(now.year, 7, 1)
kv3_end_date = datetime.date(now.year, 9, monthrange(now.year, 9)[1])
kv4_start_date = datetime.date(now.year, 10, 1)
kv4_end_date = datetime.date(now.year, 12, monthrange(now.year, 12)[1])

# Отчетный период
reporting_period_start = datetime.date(now.year, now.month, 1)
reporting_period_end = datetime.date(now.year, now.month, monthrange(now.year, now.month)[1])

# Предыдущий отчетный период
old_reporting_period_start = datetime.date(now.year, (now.month - 1 or 12), 1)
old_reporting_period_end = datetime.date(now.year, (now.month - 1 or 12), monthrange(now.year, (now.month - 1 or 12))[1])



class Department(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name="Отдел:")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'

class Admissions(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name="Поступило:")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Откуда поступило'
        verbose_name_plural = 'Откуда поступило'

class TypeComplaint(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name="Поступило:")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип обращения'
        verbose_name_plural = 'Тип обращения'

@python_2_unicode_compatible
class ClassifierOG(models.Model):
    code = models.CharField(max_length=50, verbose_name="Код:")
    title = models.CharField(max_length=600, verbose_name="Наименование:")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Классификатор ОГ'
        verbose_name_plural = 'Классификатор ОГ'


class ThemeIssues(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тематика вопроса'
        verbose_name_plural = 'Тематика вопроса'

class Complaint(models.Model):
    def get_complaint_path(self, filename):
        position = filename.rindex(".")
        name = filename[:position]
        last = filename[position:]
        path = ''.join(["complaints/files/complaint/{}/{}/{}/".format(now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")), translit.slugify(name)+last])
        return path

    def get_answer_path(self, filename):
        position = filename.rindex(".")
        name = filename[:position]
        last = filename[position:]
        path = ''.join(["complaints/files/answer/{}/{}/{}/".format(now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")), translit.slugify(name)+last])
        return path

    name = models.CharField(max_length=100, unique=True, verbose_name="Номер обращения:")
    fio = models.CharField(max_length=100, null=True, unique=False, verbose_name="ФИО:")
    address = models.CharField(max_length=100, null=True, unique=False, verbose_name="Адрес:")
    reg_date = models.DateField(db_index=True, auto_now_add=True, verbose_name="Дата поступления:")
    res_date = models.DateField(db_index=True, null=True, blank=True, verbose_name="Дата ответа:")
    description = models.TextField(verbose_name="Содержание обращения:")
    admissions = models.ForeignKey(Admissions, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Поступило:")
    in_stock = models.ForeignKey(TypeComplaint, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Тип обращения:")
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Отдел:")
    classifier_og = models.ForeignKey(ClassifierOG, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Классификатор ОГ:")

    file_complaint = models.FileField(upload_to=get_complaint_path, default="complaints/files/complaint",
                                      verbose_name="Файл вопроса:")#, validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    file_answer = models.FileField(upload_to=get_answer_path, default="complaints/files/answer",
                                   verbose_name="Файл ответа:")
    collective_appeal = models.BooleanField(default=False, db_index=True, verbose_name="Коллективное:")
    repeated_appeal = models.BooleanField(default=False, db_index=True, verbose_name="Повторное:")
    control_appeal = models.BooleanField(default=False, db_index=True, verbose_name="На контроль:")
    appeal_is_considered = models.BooleanField(default=False, db_index=True, verbose_name="Разъяснено:")
    theme_issues = models.ForeignKey(ThemeIssues, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Тематика:")

######################################### Расчет статистики по департаменту за текущий отчетный период ###########################################################

    # Количество обращений, перешедших с предыдущего периода
    def _get_stat_old_complaint_cost(self):
        return Complaint.objects.filter(admissions=2, appeal_is_considered=False, reg_date__range=(old_reporting_period_start, old_reporting_period_end)).count()

    stat_old_complaint_cost = property(_get_stat_old_complaint_cost)

    # Поступило за отчетный период
    def _get_stat_complaint_cost(self):
        return Complaint.objects.filter(admissions=2, reg_date__range=(reporting_period_start, reporting_period_end)).count()

    stat_complaint_cost = property(_get_stat_complaint_cost)

    # Поступило всего отчетный период + предыдущий период
    def _get_stat_all_cost(self):
        all_cost = self.stat_old_complaint_cost + self.stat_complaint_cost
        return all_cost

    stat_all_cost = property(_get_stat_all_cost)

    # Рассмотрено обращений в отчетном периоде
    def _get_stat_is_considered_cost(self):
        return Complaint.objects.filter(admissions=2, appeal_is_considered=True, reg_date__range=(reporting_period_start, reporting_period_end)).count()

    stat_is_considered_cost = property(_get_stat_is_considered_cost)

    # Электронные обращения
    def _get_stat_stat_type_cost(self):
        stat_type = Complaint.objects.filter(admissions=2, in_stock_id=1, reg_date__range=(reporting_period_start, reporting_period_end)).count()
        return stat_type

    stat_stat_type_cost = property(_get_stat_stat_type_cost)

    # Коллективные обращения
    def _get_stat_collective_appeal_cost(self):
        return Complaint.objects.filter(admissions=2, collective_appeal=True, reg_date__range=(reporting_period_start, reporting_period_end)).count()

    stat_collective_appeal_cost = property(_get_stat_collective_appeal_cost)

    # Повторные обращения
    def _get_stat_repeated_appeal_cost(self):
        return Complaint.objects.filter(admissions=2, repeated_appeal=True, reg_date__range=(reporting_period_start, reporting_period_end)).count()

    stat_repeated_appeal_cost = property(_get_stat_repeated_appeal_cost)

    # Обращения взятые на контроль
    def _get_stat_control_appeal_cost(self):
        return Complaint.objects.filter(admissions=2, control_appeal=True, reg_date__range=(reporting_period_start, reporting_period_end)).count()

    stat_control_appeal_cost = property(_get_stat_control_appeal_cost)


    ######################################### Тематика вопросов ########################################################
    # основы государственного управления
    def _get_stat_public_admin_cost(self):
        return Complaint.objects.filter(admissions=2, theme_issues=1, reg_date__range=(reporting_period_start, reporting_period_end)).count()

    stat_public_admin_cost = property(_get_stat_public_admin_cost)

    # социальная защита населения
    def _get_stat_social_protection_cost(self):
        return Complaint.objects.filter(admissions=2, theme_issues=2, reg_date__range=(reporting_period_start, reporting_period_end)).count()

    stat_social_protection_cost = property(_get_stat_social_protection_cost)

    # улучшение жилищных условий
    def _get_stat_housing_conditions_cost(self):
        return Complaint.objects.filter(admissions=2, theme_issues=3, reg_date__range=(reporting_period_start, reporting_period_end)).count()

    stat_housing_conditions_cost = property(_get_stat_housing_conditions_cost)

    # образование
    def _get_stat_education_cost(self):
        return Complaint.objects.filter(admissions=2, theme_issues=4, reg_date__range=(reporting_period_start, reporting_period_end)).count()

    stat_education_cost = property(_get_stat_education_cost)

    # здравоохранение
    def _get_stat_health_cost(self):
        return Complaint.objects.filter(admissions=2, theme_issues=5, reg_date__range=(reporting_period_start, reporting_period_end)).count()

    stat_health_cost = property(_get_stat_health_cost)

    # ЖКХ
    def _get_stat_hcs_cost(self):
        return Complaint.objects.filter(admissions=2, theme_issues=6, reg_date__range=(reporting_period_start, reporting_period_end)).count()

    stat_hcs_cost = property(_get_stat_hcs_cost)

    # законность и правопорядок
    def _get_stat_law_and_order_cost(self):
        return Complaint.objects.filter(admissions=2, theme_issues=7, reg_date__range=(reporting_period_start, reporting_period_end)).count()

    stat_law_and_order_cost = property(_get_stat_law_and_order_cost)

    # иные
    def _get_stat_other_cost(self):
        return Complaint.objects.filter(admissions=2, theme_issues=8, reg_date__range=(reporting_period_start, reporting_period_end)).count()

    stat_other_cost = property(_get_stat_other_cost)
######################################################################################################################

    def save(self, *args, **kwargs):
        try:
            this_records = Complaint.objects.get(pk=self.pk)
            for this_record in this_records:
                if this_record.file_complaint != self.file_complaint:
                    this_record.file_complaint.delete(save=False)
        except:
            pass
        super(Complaint, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file_complaint.delete(save=False)
        super(Complaint, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("complaints_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "жалобы"
        verbose_name_plural = "жалобы"
        permissions = (
            ("can_administrator", "Доступ только для администраторов"),
            ("can_customers", "Доступ только для пользователей"),
        )
