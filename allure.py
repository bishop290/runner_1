# -*- coding: utf8 -*
import sys
from os import listdir
from subprocess import call


def write_string_file(filename, param_write, wr_str):
    '''
    filename - полный путь с именем до файла
    param_write - параметр записа 'w' - заменяет содержимое в файле 'a' - добавляет к содержимому в файле
    wr_str - строка которую записываем в файл
    *
    записывает строку в файл на компьютере
    '''
    with open(filename, param_write, encoding="utf8") as my_file:
        my_file.write(wr_str)
    my_file.close()


def main_func(argv_list):
    #argv_list = ['', 'RUN_2.3.4']

    if len(argv_list) != 2:
        exit()

    dir_allure = 'D:\\allure'
    index_file = dir_allure + '\\index.html'

    wr_str = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
</head>
<body>
<h1>ТЕСТЫ</h1>\n
<b>
'''
    write_string_file(index_file, 'w', wr_str)

    my_line = '<p>'
    try:
        with open(dir_allure + '\\log_spent_tests.txt', "r", encoding='utf-8') as my_file:
            for line in my_file:
                if line == '':
                    my_line = my_line + '</p><p>'
                else:
                    my_line = my_line + '<br>' + line
        my_file.close()
    except:
        print("log_spent_tests.txt --- не считан")
    my_line = my_line + '</p>'
    write_string_file(index_file, 'a', my_line + '</b>')

    dir_list = listdir(dir_allure)
    counter = 0
    for dir_str in dir_list:
        if dir_str.find(argv_list[1]) != -1:
            folder_name = str(counter)
            str_proc = "\"C:\\Users\\Kuznetsov_G\\Desktop\\allure-2.13.2\\bin\\allure\" generate \"{0}\{1}\" -o \"{0}\{2}\" --clean".format(dir_allure, dir_str, folder_name)
            print(str_proc)
            call(str_proc, shell=True)
            wr_str = '<p><a href=\"{0}\index.html\">{1}</a></p>\n'.format(folder_name, dir_str)
            write_string_file(index_file, 'a', wr_str)
            counter = counter + 1

    wr_str = '''
</body>
</html>
'''
    write_string_file(index_file, 'a', wr_str)


if __name__ == "__main__":
    main_func(sys.argv)