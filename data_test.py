import sys, os
import psycopg2
import postgresql
import random
import time


def strTimeProp(start, end, format, prop):
    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(format, time.localtime(ptime))

def randomDate(start, end, prop):
    return strTimeProp(start, end, '%Y-%m-%d', prop)


# Добавить в базу тестовые данные за период
def insertdb():
    try:
        conn = psycopg2.connect(dbname='django_coc_db', user='postgres', password='31yu*#km', host='127.0.0.1', port='5432')
        cursor = conn.cursor()

        for i in range(1, 100):

            cursor.execute("""
                    INSERT INTO complaints_complaint (name, fio, address, reg_date, res_date, description,
                    file_complaint, file_answer, admissions_id, in_stock_id, classifier_og_id, group_id,
                    collective_appeal, control_appeal, repeated_appeal, appeal_is_considered, theme_issues_id)
                    VALUES (%(name)s, %(fio)s, %(address)s, %(reg_date)s, %(res_date)s, %(description)s, 
                    %(file_complaint)s, %(file_answer)s, %(admissions_id)s, %(in_stock_id)s, %(classifier_og_id)s, 
                    %(group_id)s, %(collective_appeal)s, %(control_appeal)s, %(repeated_appeal)s, 
                    %(appeal_is_considered)s, %(theme_issues_id)s);
                    """,
                        {'name': "ДСЗН-{}-1-1".format(i),
                         'fio': "Бородулин Д.А.",
                         'address': "600022, г. Владимир, ул. Крайнова 3а, кв. 76",
                         'reg_date': randomDate("2019-01-01", "2019-01-27", random.random()),
                         'res_date': randomDate("2019-01-01", "2019-01-27", random.random()),
                         'description': "Тестовое обращение",
                         'file_complaint': "complaints/files/complaint/2019/01/27/test.pdf",
                         'file_answer': "complaints/files/complaint/2019/01/27/test.pdf",
                         'admissions_id': random.randint(1, 3),
                         'in_stock_id': random.randint(1, 2),
                         'classifier_og_id': random.randint(795, 2468),
                         'group_id': random.randint(1, 12),
                         'collective_appeal': random.choice([True, False]),
                         'control_appeal': random.choice([True, False]),
                         'repeated_appeal': random.choice([True, False]),
                         'appeal_is_considered': random.choice([True, False]),
                         'theme_issues_id': random.randint(1, 8)
                         })
            conn.commit()

    except psycopg2.Error as err:
        print("Connection error: {}".format(err))