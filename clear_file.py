# Скрипт чистит файлы если на них нет ссылки в базе

import sys, os
import psycopg2
import postgresql
import random
import time

file_links = []
dir_work = []
DIR = r'C:\site\COC\uploads\complaints\files'





def selectdb():
    try:
        conn = psycopg2.connect(dbname='django_coc_db', user='postgres', password='31yu*#km', host='127.0.0.1', port='5432')
        cursor = conn.cursor()
        cursor.execute("SELECT reg_date, file_complaint, file_answer FROM complaints_complaint",)
        rows = cursor.fetchall()
        for row in rows:
            file_links.append(row)

    except psycopg2.Error as err:
        print("Connection error: {}".format(err))


# Сканировать папки
def ScanDir(dir):
    global dir_work
    for root, dirs, files in os.walk(dir):
        # print(root)
        dir_work.append(root)
    return dir_work

def ScanFileALL(dir_root):
    for dir in dir_root:
        names = os.listdir(dir)   # список файлов и поддиректорий в данной директории
        for name in names:
            fullname = os.path.join(dir, name)  # получаем полное имя
            if os.path.isfile(fullname):        # если это файл...
                file = fullname.replace("\\","/")
                for file_link in file_links:

                    if not file[20:] in file_link:
                        print("На Файл {} нет ссылки, удалить".format(file[20:]))
                        os.remove(fullname)

if __name__ == '__main__':
    selectdb()
    #ScanDir(DIR)
    #ScanFileALL(dir_work)
    #complaints/files/complaint/2017/10/05/dszn-399-05-07.pdf