# -*- coding: utf8 -*
#10mar20kg
#python 3.7.1

from proc import proc, dif_proc
from shutil import rmtree
from os import path, listdir, mkdir
from log import log_save
from time import sleep


'''
prepare.py - консольные команды копирования, подключения, удаление, чтение и запись файлов
'''



def del_path(cur_path, params):
    '''
    cur_path - директория которую нужно удалить
    *
    удаляет директорию
    '''
    if path.exists(cur_path):
        log_save('DEL ' + cur_path, params)
        rmtree(cur_path)
    else:
        log_save('NOT DEL ' + cur_path, params)



def just_do_it(command, param_dict, about='', p_1c='', client=None):
    '''
    command - консольная команда
    about - строка описыват что делаем
    p_1c=''
    *
    запускает консольную команду в процессе
    '''
    log_save(about + ' : ' + command, param_dict)
    proc(command, p_1c, False, client)



def prepare_st(param_dict):
    '''
    param_dict - словарь параметров
    *
    устанавливает кодировку в консоли для русских символов
    подключается к указанным компьютерам
    копирует платформу на компьютер где будет прохолить тест
    копирует Ванессу на компьютер где будет прохолить тест
    копирует тесты, конфигурацию и эталоны на компьютер где будет прохолить тест
    создает директорию для логфайлов
    '''
    client = param_dict['CLIENT']
    NET_USER = param_dict['NET_USER']
    NET_DOMAIN = param_dict['NET_DOMAIN']
    NET_PASSWORD = param_dict['NET_PASSWORD']
    TESTS_ON_RUNNER = param_dict['TESTS_ON_RUNNER']
    WORK_PATH = param_dict['WORK_PATH']
    TEST_CATALOG = param_dict['TEST_CATALOG']
    PREPARE_MODE = param_dict['PREPARE_MODE']
    REPORTS_PATH = param_dict['REPORTS_PATH']
    MODEL_ON_RUNNER = param_dict['MODEL_ON_RUNNER']

    if not path.exists(TEST_CATALOG):
        log_save('CREATE : ' + TEST_CATALOG, param_dict)
        mkdir(TEST_CATALOG)

    xcopy_template = 'XCOPY \"{0}\" \"{1}\"  /H /Y /C /R /S /J /Q'
    copy_from_test_repo = 'XCOPY \"{0}\\tests_git\" \"{1}\"  /H /Y /C /R /S /J /Q'.format(REPORTS_PATH, TESTS_ON_RUNNER)
    copy_from_tests = xcopy_template.format(param_dict['TESTS_PATH'], TESTS_ON_RUNNER)

    if PREPARE_MODE == 'uprep+ret':
        #удаляем все эталонные базы
        path_list = listdir(MODEL_ON_RUNNER)
        for i in path_list:
            curr_path  = MODEL_ON_RUNNER + i
            if path.isdir(curr_path):
                del_path(curr_path, param_dict)
        #или скачиваем все исходники
    else:
        if NET_DOMAIN != '':
            just_do_it('net use', param_dict, 'NET')
            just_do_it('net use /delete * /y', param_dict, 'NET')
        
            net_con_1 = 'net use {0} /PERSISTENT:NO /User:{1}\\{2} {3}'.format(param_dict['BUILD_FILES_Trunk'], NET_DOMAIN, NET_USER, NET_PASSWORD)
        
            just_do_it(net_con_1, param_dict, 'NET CON')
            just_do_it('net use', param_dict, 'NET')

        copy_platform = xcopy_template.format(param_dict['PLATFORM_PATH'], param_dict['PLATFORM_PATH_ON_RUNNER'])
        copy_vanessa = xcopy_template.format(param_dict['VANESSA_PATH'], param_dict['VANESSA_ON_RUNNER'])
        copy_vanessa_tools = xcopy_template.format(param_dict['VANESSA_TOOLS'], param_dict['VANESSA_TOOLS_ON_RUNNER'])
        copy_all_dt = xcopy_template.format(param_dict['MODEL_PATH'], param_dict['MODEL_ON_RUNNER'])
        copy_cf = xcopy_template.format(param_dict['CF_PATH'], WORK_PATH )

        command_list = [[just_do_it, [copy_platform, param_dict, 'COPY PLATFORM']],
                        [just_do_it, [copy_vanessa, param_dict, 'COPY VANESSA']],
                        [just_do_it, [copy_vanessa_tools, param_dict, 'COPY VANESSA TOOLS']],
                        [just_do_it, [copy_all_dt, param_dict, 'COPY ALL DT']],
                        [just_do_it, [copy_cf, param_dict, 'COPY CF']]]
    
        proc_list = []
        proc_list_append = proc_list.append
        for list_i in command_list:
            if list_i[1][1] == 'COPY CF':
                if PREPARE_MODE == 'cpcf':
                    proc_list_append(dif_proc(list_i[0], list_i[1]))
                else:
                    if not path.exists(WORK_PATH):
                        mkdir(WORK_PATH)
            else:
                proc_list_append(dif_proc(list_i[0], list_i[1]))
            sleep(1)

        for proc in proc_list:
            proc.join()

    #создание каталога с отчетами
    if not path.exists(REPORTS_PATH):
        log_save('CREATE : ' + REPORTS_PATH, param_dict)
        mkdir(REPORTS_PATH)
    log_dir = '{0}\\log_{1}'.format(REPORTS_PATH, param_dict['CONF'])
    if not path.exists(log_dir):
        log_save('CREATE : ' + log_dir, param_dict)
        mkdir(log_dir)

    #копирование автотестов
    if param_dict['GIT_REPO_TESTS'] != '':
        if path.exists(REPORTS_PATH + '\\tests_git'):
            just_do_it('cd "' + REPORTS_PATH + '\\tests_git" & git pull origin master > cmd', param_dict, 'GIT PULL')
        else:
            just_do_it('cd ' + REPORTS_PATH + ' & git clone "' +\
                       param_dict['GIT_REPO_TESTS'] + '" "tests_git" > cmd', param_dict, 'GIT CLONE')

        just_do_it(copy_from_test_repo, param_dict, 'COPY FROM TEST REPO')
    else:
        just_do_it(copy_from_tests, param_dict, 'COPY TESTS')



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



def write_list_file(enter_list, filename, param_write):
    '''
    enter_list - список со строками
    filename - полный путь с именем до файла
    param_write - параметр записа 'w' - заменяет содержимое в файле 'a' - добавляет к содержимому в файле
    *
    записывает список состоящий из строк в файл на компьютере
    '''
    with open(filename, param_write, encoding="utf8") as my_file:
        my_file_write = my_file.write
        for i in enter_list:
            my_file_write(i)
    my_file.close()



def open_file_r(filename, enc="utf8"):
    '''
    filename - полный путь с именем до файла
    *
    читает файл на компьютере
    *
    return file_list - возвращает список с прочитанными строками
    '''
    file_list = []
    file_list_append = file_list.append
    with open(filename, "r", encoding=enc) as my_file:
        for line in my_file:
            file_list_append(line)
    my_file.close()

    if len(file_list) == 0:
        print("empty file: " + filename + '\n')

    return file_list



def get_cd_directory(name, dir_path):
    '''
    name - строка содержащаяся в названии директории
    dir_path - директория в которой ищем
    *
    ищет название поддиректорию по заданной строке
    *
    возвращает путь до найденной папки либо пустую строку
    '''
    result = ''
    dir_list = listdir(dir_path)
    for i in dir_list:
        if i.find(name) != -1:
            result = dir_path + "\\" + i
    return result
