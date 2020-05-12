# -*- coding: utf8 -*
#04mar20kg
#python 3.7.1

from shutil import copyfile
from os import mkdir, path
from time import sleep

from proc import proc
from test_pars import va_params
from prepare import write_string_file, del_path, get_cd_directory
from log import log_save


'''
dt.py - работа с 1С через командную строку
'''



def just_do_it(command, param_dict, wait_1c='', about='', kill=False, client=None):
    '''
    command - консольная команда
    wait_1c - имя процесса 1с, если нужно ждать 1с
    about - строка описыват что делаем
    kill - если нужно убить процесс
    *
    запускает консольную команду в процессе
    '''
    log_save(about + ' : ' + command, param_dict)
    if param_dict['FLAG_ERROR_START'] == False:
        result = proc(command, wait_1c, kill, client)
    else:
        result = proc(command)
    return result



def create_base(param_dict, base_use, name_dir=''):
    '''
    param_dict - словарь параметров
    base_use - строка, вид базы manager или client
    name_dir - имя папки с базой
    *
    создает пустую базу
    '''
    path = ''
    if base_use == 'manager':
        path = param_dict['WORK_PATH_BASE_M']

    elif base_use == 'client':
        param_dict['WORK_PATH_BASE_CURR'] = '{0}\\{1}'.format(param_dict['WORK_PATH_BASE_C'], name_dir)
        path = param_dict['WORK_PATH_BASE_CURR']

        if param_dict['PREPARE_MODE'] == 'uprep+ret':
            del_path(path, param_dict)

    comm_str = '{0} CREATEINFOBASE File={1}'.format(param_dict['START_PL_1C'], path)
    just_do_it(comm_str, param_dict, '1cv8.exe', 'CREATE BASE: ' + base_use, False, param_dict['CLIENT'])



def eat_dt(param_dict, base_use, usr=''):
    '''
    param_dict - словарь параметров
    base_use - строка, вид базы manager или client
    usr - пользователь базы
    *
    загружает dt файл в базу
    '''
    if base_use == 'manager':
        dt = param_dict['MODEL_ON_RUNNER'] + 'manager.dt'
        path = param_dict['WORK_PATH_BASE_M']
    elif base_use == 'client':
        dt = param_dict['MODEL_ON_RUNNER_CURRENT_DT']
        path = param_dict['WORK_PATH_BASE_CURR']

    comm_str = '{STARTER_1C} DESIGNER /F {DB_PATH} /N"{USER}" /P"" /RestoreIB {DT_PATH} /Out {LOG_PATH} /Visible'.format(
        STARTER_1C = param_dict['START_1cestart'],
        DB_PATH = path,
        USER = usr,
        DT_PATH = dt,
        LOG_PATH = param_dict['LOG_PATH'])

    just_do_it(comm_str, param_dict, '1cv8.exe', 'LOAD DT: ' + base_use, False, param_dict['CLIENT'])



def dump_cf(param_dict):
    '''
    param_dict - словарь параметров
        *
    выгружает cf
    '''

    comm_str = '{STARTER_1C} DESIGNER /F {DB_PATH} /N"{USER}" /P"" /DumpCfg {CF_PATH}1Cv8.cf /Out {LOG_PATH} /Visible'.format(
        STARTER_1C = param_dict['START_1cestart'],
        DB_PATH = param_dict['WORK_PATH_BASE_CURR'],
        USER = param_dict['MODEL_ADMIN_USER'],
        CF_PATH = param_dict['WORK_PATH'],
        LOG_PATH = param_dict['LOG_PATH'])

    just_do_it(comm_str, param_dict, '1cv8.exe', 'DUMP CF', False, param_dict['CLIENT'])



def updt(param_dict):
    '''
    param_dict - словарь параметров
        *
    обновляет базу
    '''

    comm_str = '{STARTER_1C} DESIGNER /F {PATH_BASE} /N"{USER}" /P"" /UpdateDBCfg /Out {LOG_PATH} /Visible'.format(
        STARTER_1C = param_dict['START_1cestart'],
        PATH_BASE = param_dict['WORK_PATH_BASE_CURR'],
        USER = param_dict['MODEL_ADMIN_USER'],
        LOG_PATH = param_dict['LOG_PATH'])

    just_do_it(comm_str, param_dict, '1cv8.exe', 'UPDT CF', False, param_dict['CLIENT'])



def eat_cf(param_dict):
    '''
    param_dict - словарь параметров
    *
    загружает и обновляет cf файл 
    '''

    comm_str = '{STARTER_1C} DESIGNER /F {PATH_BASE} /N"{USER}" /P"" /LoadCfg {WORK_PATH}1Cv8.cf /Out {LOG_PATH} /Visible'.format(
        STARTER_1C = param_dict['START_1cestart'],
        PATH_BASE = param_dict['WORK_PATH_BASE_CURR'],
        USER = param_dict['MODEL_ADMIN_USER'],
        WORK_PATH = param_dict['WORK_PATH'],
        LOG_PATH = param_dict['LOG_PATH'])

    just_do_it(comm_str, param_dict, '1cv8.exe', 'LOAD CF', False, param_dict['CLIENT'])
    updt(param_dict)



def upd_from_repo(param_dict):
    '''
    param_dict - словарь параметров
    *
    обновляет базу из хранилища
    '''

    comm_str = '{PLATFORM} DESIGNER /F "{PATH_BASE}" /N"{USER}" /P"" /ConfigurationRepositoryF"{REPO_PATH}" /ConfigurationRepositoryN"{REPO_USER}" /ConfigurationRepositoryP"{REPO_PASSWORD}" /ConfigurationRepositoryUpdateCfg -v"{REPO_VER}" /Visible /Out {LOG_PATH}'.format(
        PLATFORM = param_dict['START_PL_1C'],
        PATH_BASE = param_dict['WORK_PATH_BASE_CURR'],
        USER = param_dict['MODEL_ADMIN_USER'],
        REPO_PATH = param_dict['REPO_PATH'],
        REPO_USER = param_dict['REPO_USER'],
        REPO_PASSWORD = param_dict['REPO_PASSWORD'],
        REPO_VER = param_dict['REPO_VER'],
        LOG_PATH = param_dict['LOG_PATH'])

    just_do_it(comm_str, param_dict, '1cv8.exe', 'UPD FROM REPO', False, param_dict['CLIENT'])
    updt(param_dict)



def start_vanessa(param_dict, test_name, kill=True, global_test_name=''):
    '''
    param_dict - словарь параметров
    test_name - имя теста, присваивается автоматически в зависимости от тэгов расставленых в фича-файле
    например: "@_$Наценка-сумма-строка"
    kill -
    *
    подготавливает конфиг для Ванессы
    запускает Ванессу с нужным тестом
    создает лог запуска теста
    '''
    VAParams = va_params(param_dict, test_name)
    path_VAParams = param_dict['TESTS_ON_RUNNER'] + 'VAParams.json'
    path_VAParams = path_VAParams.replace('\\', '\\\\')

    write_string_file(path_VAParams, 'w', VAParams)

    comm_str = '{PLATFORM} ENTERPRISE /F {PATH_BASE} /DEBUG /AllowExecuteScheduledJobs -Off /DisableStartupDialogs /DisableStartupMessages /N"Администратор" /P"" /Execute {VANNESSA_EPF} /TESTMANAGER /C"StartFeaturePlayer;VBParams={VANESSA_PARAMS}" /Out {LOG_PATH}'.format(
        PLATFORM = param_dict['START_PL_1C'],
        PATH_BASE = param_dict['WORK_PATH_BASE_M'],
        VANNESSA_EPF = param_dict['VANNESSA_EPF'],
        VANESSA_PARAMS = path_VAParams,
        LOG_PATH = param_dict['LOG_PATH'])

    result = just_do_it(comm_str, param_dict, '1cv8.exe', 'CALL VANESSA', kill, param_dict['CLIENT'])

    if param_dict['FLAG_ERROR_START'] == False:
        log_name = '{0}\\log_{1}\\LOG_{2}({3}).txt'.format(param_dict['REPORTS_PATH'], param_dict['CONF'], test_name, global_test_name)
        log_save('CREATE LOG: ' + log_name + '\n', param_dict)
        copyfile(param_dict['LOG_PATH'] , log_name)
    return result



def reject_cd(param_dict, dt_name=''):
    '''
    param_dict - словарь параметров
    dt_name - ('role.dt') имя базы-эталона для данного тестирования
    *
    копирует CD файл клиентской базы в каталог шаблонов
    '''
    WORK_PATH_BASE_CURR = param_dict['WORK_PATH_BASE_CURR']

    storage_path = param_dict['MODEL_ON_RUNNER'] + 'storage_' + dt_name + '\\'
    if not path.exists(storage_path):
        mkdir(storage_path)

    comm_str = 'XCOPY "{0}\\*1Cv8.1CD" "{1}"  /H /Y /C /R /S /J '.format(WORK_PATH_BASE_CURR, storage_path)
    just_do_it(comm_str, param_dict, 'xcopy.exe', 'DUMP', False, param_dict['CLIENT'])

    param_dict['STORAGE_CURR_1CD'] = 'storage_' + dt_name



def push_cd_client(param_dict, flag_curr_path_cd=''):
    '''
    param_dict - словарь параметров
    flag_curr_path_cd - директория где лежит чистый, обновленный эталон
    *
    удаляет файлы клиентской базы
    копирует CD файл клиентской базы из каталога шаблонов в расположение клиентской базы
    '''
    WORK_PATH_BASE_CURR = param_dict['WORK_PATH_BASE_CURR']

    if flag_curr_path_cd == '':
        flag_curr_path_cd = param_dict['MODEL_ON_RUNNER'] + '\\' + param_dict['STORAGE_CURR_1CD']

    del_path(WORK_PATH_BASE_CURR, param_dict)
    sleep(1)
    mkdir(WORK_PATH_BASE_CURR)
    sleep(1)

    comm_str = 'XCOPY "{0}\\*1Cv8.1CD" "{1}\\"  /H /Y /C /R /S /J '.format(flag_curr_path_cd, WORK_PATH_BASE_CURR)
    just_do_it(comm_str, param_dict, 'xcopy.exe', 'PUSH', False, param_dict['CLIENT'])


