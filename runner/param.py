# -*- coding: utf8 -*
#04mar20kg
#python 3.7.1

from os import listdir, path, getpid, remove
from log import log_save
from datetime import datetime

from prepare import open_file_r

'''
param.py - все настройки программы (сценарии+параметры)
'''


def menu_cicle(mess_str, curr_list):
    '''
    '''
    count = 0
    flag_first_menu = True
    while flag_first_menu:
        print('{0}\nили введи ext для выхода\n'.format(mess_str))
        for i in curr_list:
            print('{0}) {1}'.format(str(count), i))
            count = count + 1
        count = 0
        num = input(': ')
        if num == 'ext':
            exit()
        try:
            curr_config = curr_list[int(num)]
            flag_first_menu = False
        except:
            print('..еще раз.\n')
            continue
    return curr_config



def ret_param_dict(sys_argv_list):
    '''
    '''
    current_directory = path.abspath(__file__)   
    current_directory = path.split(current_directory)[0]
    
    #очистка логов
    #log = current_directory + '\\main_log.log'
    #if path.isfile(log):
        #remove(log)
        
    current_directory = path.split(current_directory)[0]
    
    #запуск с параметрами или без
    len_argv_list = len(sys_argv_list)
    if len_argv_list == 4:
        config = sys_argv_list[1]
        scen = sys_argv_list[2]
        ver_conf = sys_argv_list[3]
        if len(ver_conf) >= 50:
            print('нельзя вводить больше 50 знаков\n')
            exit()
    elif len_argv_list < 4 and len_argv_list > 1 or len_argv_list > 4:
        print('неправильное количество параметров в команде\n')
        exit()
    else:
        configs_list = []
        scen_list = []

        dir_list = listdir(current_directory)
        
        for i in dir_list:
            if i.find('config_') != -1:
                configs_list.append(i)
            elif i.find('scen_') != -1:
                scen_list.append(i)
        
        #консольное меню------------------------------------------------------------------------------------------------------------
        config = menu_cicle('\nВыбери номер конфигурационного файла: \n', configs_list)
        scen = menu_cicle('\nВыбери номер файла со сценарием: \n', scen_list)
        
        ver_conf = input('\nВведи имя текущего прогона: ')
        if len(ver_conf) >= 50:
            print('нельзя вводить больше 50 знаков\n')
            exit()
        #---------------------------------------------------------------------------------------------------------------------------

    #читаем файлы с настройками
    config = open_file_r(current_directory + '\\' + config)
    scen = open_file_r(current_directory + '\\' + scen)
    
    #кортежи для проверки обязательности заполнения настройки, если True то настройка обязательна
    config_params_names = (('PREPARE_MODE', True), ('BUILD_FILES', True), ('PLATFORM_NUMBER', True), ('PLATFORM_PATH', True), 
                           ('STARTER_1C', True), ('NET_DOMAIN', False), ('NET_USER', False), ('NET_PASSWORD', False), ('REPO_PATH', False), 
                           ('REPO_VER', False), ('REPO_USER', False), ('REPO_PASSWORD', False), ('GIT_REPO_TESTS', False), ('REPORTS', False),
                           )
    scen_params_names = (('ЭТАЛОН', 'DT', True), ('ПОЛЬЗОВАТЕЛЬ С ПОЛНЫМИ ПРАВАМИ', 'ADM_USER', True), ('ПОЛЬЗОВАТЕЛЬ ДЛЯ ТЕСТА', 'USER', True), 
                         ('ФАЙЛ С ТЕСТОМ', 'TEST_FILE', True), ('ПРИКРЕПИТЬ ДОП. ТЕСТ В НАЧАЛО', 'ADD_HEAD', False), 
                         ('ПРИКРЕПИТЬ ДОП. ТЕСТ В КОНЕЦ', 'ADD_TAIL', False), ('ПОЧТА', 'ADDR', False), ('ЗАМЕНА СТРОКИ', 'SWAP_CURR_STR', False),
                         )
    #пустые словари для первоначальных настроек
    first_params = dict(PREPARE_MODE = '', BUILD_FILES = '', PLATFORM_NUMBER = '', PLATFORM_PATH = '', 
                           STARTER_1C = '', NET_DOMAIN = '', NET_USER = '', NET_PASSWORD = '', REPO_PATH = '', 
                           REPO_VER = '', REPO_USER = '', REPO_PASSWORD = '', GIT_REPO_TESTS = '', REPORTS = '')
    
    one_test_params = dict(PREPARE_MODE = '', DT = '', ADM_USER = '', USER = '', TEST_FILE = '',
                           ADD_HEAD = '', ADD_TAIL = '', ADDR = '', SWAP_CURR_STR = [])
    
    #заполнение первоначальных настроек из считанных файлов---------------------------------------------------------------------
    #заполнение настроек
    scenario_list = []
    for param_tuple in config_params_names:
        for i_str in config:
            param = param_tuple[0]
            control_str = i_str[0:3]
            if control_str.find('#') == -1 and i_str.find(param) != -1:
                val = i_str.split('=')[1]
                val = val.strip('\n')
                val = val.strip(' ')
                if val == '' and param_tuple[1]:
                    print('\nне заполнен обязательный параметр {0}\nзавершение работы\n'.format(param))
                    exit()
                first_params[param] = val
                break

    #заполнение настроек сценариев
    test_counter = 1
    for i_str in scen:
        control_str = i_str[0:3]
        if control_str.find('#') == -1 and i_str.find('ЭТАЛОН') != -1:
            if one_test_params['TEST_FILE'] != '':
                # когда второй раз находит слово ЭТАЛОН. 
                # то в настройки первого теста добавляет PREPARE_MODE, в остальных будет ret 
                if test_counter == 2:
                    one_test_params['PREPARE_MODE'] = first_params['PREPARE_MODE']
                else:
                    one_test_params['PREPARE_MODE'] = 'ret'
                test_counter = test_counter + 1

                scenario_list.append(one_test_params.copy())

            for i in one_test_params:
                one_test_params[i] = ''
                
            val = i_str.split('=')[1]
            val = val.strip('\n')
            val = val.strip(' ')
            if val == '':
                print('\nне заполнен обязательный параметр ЭТАЛОН\nзавершение работы\n')
                exit()
            one_test_params['DT'] = val
            test_counter = test_counter + 1
        
        elif control_str.find('#') == -1:
            for param_tuple in scen_params_names:
                param = param_tuple[0]
                name_param = param_tuple[1]
                if i_str.find(param) != -1:
                    val = i_str.split('=')[1]
                    val = val.strip('\n')
                    val = val.strip(' ')
                    if val == '' and param_tuple[2]:
                        print('\nне заполнен обязательный параметр {0}\nзавершение работы\n'.format(param))
                        exit()
                    if param == 'ЗАМЕНА СТРОКИ':
                        val_list = val.split(',')
                        cr_ls = []
                        final_swap_list = []
                        for i in val_list:
                            i = i.strip(' ')
                            cr_ls.append(i)
                            if len(cr_ls) == 2:
                                final_swap_list.append(cr_ls.copy())
                                cr_ls = []
                        one_test_params[name_param] = final_swap_list
                    else:    
                        one_test_params[name_param] = val
                    break
    if one_test_params['TEST_FILE'] != '':
        if test_counter == 2: # если тест всего один то значение счетчика должно быть 2
            one_test_params['PREPARE_MODE'] = first_params['PREPARE_MODE']
        else:
            one_test_params['PREPARE_MODE'] = 'ret'
        scenario_list.append(one_test_params.copy())
    #---------------------------------------------------------------------------------------------------------------------------
    
    if first_params['REPORTS'] == '':
        first_params['REPORTS'] = current_directory + '\\REPORTS'

    pid_curr_proc = str(getpid())
    platform_number = first_params['PLATFORM_NUMBER']   
    platform = first_params['PLATFORM_PATH'] + platform_number
    build_files = first_params['BUILD_FILES']
    storage = current_directory + '\\TEST_CATALOG'
    work = storage + '\\work\\'

    #финальный словарь с настройками-------------------------------------------------------------------------------------------
    param_dict = dict(CONF = ver_conf,
                      BUILD_FILES_Trunk = build_files,
                      PLATFORM_PATH = build_files + '\\platforms\\' + platform_number,
                      PLATFORM_PATH_ON_RUNNER = platform + '\\',
                      START_PL_1C = '\"' + platform + '\\bin\\1cv8.exe\"',
                      PID = pid_curr_proc,
                      START_1cestart = '"{0}"'.format(first_params['STARTER_1C']),
                      CURR_DIR = current_directory + '\\',
                      VANESSA_PATH = build_files+'\\vanessa\\vanessa-automation',
                      VANESSA_TOOLS = build_files+'\\vanessa\\vanessa-tools',
                      TEST_CATALOG = storage,
                      VANESSA_ON_RUNNER = storage + '\\vanessa\\vanessa-automation\\',
                      VANESSA_TOOLS_ON_RUNNER = storage + '\\vanessa\\vanessa-tools\\',
                      VANNESSA_EPF = storage + '\\vanessa\\vanessa-automation\\vanessa-automation.epf',
                      TESTS_PATH = build_files + '\\tests',
                      TESTS_ON_RUNNER = storage + '\\tests\\',
                      MODEL_PATH = build_files + '\\model',
                      MODEL_ON_RUNNER = storage + '\\model\\',
                      MODEL_ON_RUNNER_CURRENT_DT = '',
                      WORK_PATH = work,
                      WORK_PATH_BASE_M = work + 'base_M',
                      WORK_PATH_BASE_C = work + 'base_C',
                      WORK_PATH_BASE_CURR = '',
                      CF_PATH = build_files + '\\cf',
                      LOG_PATH = work + 'log.txt',
                      MODEL_ADMIN_USER = '',
                      MODEL_USER = '',

                      NET_DOMAIN = first_params['NET_DOMAIN'],
                      NET_USER = first_params['NET_USER'],
                      NET_PASSWORD = first_params['NET_PASSWORD'],

                      REPO_PATH = first_params['REPO_PATH'], 
                      REPO_VER = first_params['REPO_VER'],
                      REPO_USER = first_params['REPO_USER'],
                      REPO_PASSWORD = first_params['REPO_PASSWORD'],

                      GIT_REPO_TESTS = first_params['GIT_REPO_TESTS'],

                      ESC_VANESSA = 'Истина',
                      ESC_TEST_CLIENT = 'Истина',
                      STORAGE_CURR_1CD = '',

                      # замеры времени начала и окончания прогона
                      START_TIME = '',
                      END_TIME = '',
                      
                      PREPARE_MODE = '',
                      # хранит объект "клиент" с подключением к порту 
                      CLIENT = None,

                      # хранит имя теста и имя пользователя от него
                      # [0] - имя теста, [1] - имя ползователя, [2] - False если тест еще не использовался, 
                      # [3] - False если ошибок не было, [4] - имя использующегося DT файла (оно же имя папки с чистой базой под тест)
                      TEST_USER_LIST = [],
                      #если истина то запуск происходит без контроля завершения и не пишутся логи (для воспроизведения упавших тестов)
                      FLAG_ERROR_START = False,

                      REPORTS_PATH = first_params['REPORTS'],

                      SCEN = scenario_list
    )
    #--------------------------------------------------------------------------------------------------------------------------
    log_save('текущая директория: ' + current_directory, param_dict)
    log_save('MAIN PID : ' + pid_curr_proc, param_dict)

    return param_dict

