# -*- coding: utf8 -*
#10mar20kg
#python 3.7.1

import sys
from datetime import datetime
from os import path
from time import sleep

from param import ret_param_dict
from prepare import (prepare_st, 
                     del_path, 
                     write_string_file,
                     open_file_r)
from dt import (create_base, 
                eat_cf, 
                eat_dt, 
                start_vanessa, 
                reject_cd,
                push_cd_client,
                upd_from_repo,
                dump_cf)
from test_pars import update_test, prepare_tests, print_cat
from proc import kill_1C, proc_prior, proc, start_servo, start_client, kill_python
from mail import send_mail
from log import log_save

'''
main.py - основные функции программы.
'''


def update_dt(params):
    '''
    params - словарь параметров
    *
    обновляет базу на cf или из репозитория
    собирает тест для обновления в режиме предприятия
    запускает Ванессу для обновления базы в режиме предприятие
    '''
    flag_cf = True
    PREPARE_MODE = params['PREPARE_MODE']

    if PREPARE_MODE == 'uprep':
        flag_cf = path.isfile(params['WORK_PATH']+'\1Cv8.cf')
        if flag_cf:
            eat_cf(params)
        else:
            upd_from_repo(params)

    elif PREPARE_MODE == 'uprep+ret':
        upd_from_repo(params)

    else:
        eat_cf(params)

    test_string = update_test(params)
    write_string_file(params['TESTS_ON_RUNNER'] + 'prepare.feature', 
                      'w', 
                      test_string
                      )

    start_vanessa(params, 'prepare.feature')
    if flag_cf == False:
        dump_cf(params)



def start_tests(params, test_name, addit_strings_head_rmk, addit_strings_tail, flag_curr_path_cd='', SWAP_CURR_STR = [], DT=''):
    '''
    params - словарь параметров
    test_name - имя общего теста который запускаем
    addit_strings_head - имя файла с тестом, тест прикрепляющийся к началу основного теста, если нужно
    addit_strings_tail - имя файла с тестом, тест прикрепляющийся к концу основного теста, если нужно
    *
    собирает основные тесты для запуска
    на обнавленном эталоне запускает тесты в цикле
    '''
    if params['WORK_PATH_BASE_CURR'] == '':
        WORK_PATH_BASE_CURR = params['WORK_PATH_BASE_C'] + '\\' + DT
        if not path.exists(WORK_PATH_BASE_CURR):
            mkdir(WORK_PATH_BASE_CURR)
        params['WORK_PATH_BASE_CURR'] = WORK_PATH_BASE_CURR    
    
    prepare_tests(params, test_name, addit_strings_head_rmk, addit_strings_tail, SWAP_CURR_STR, DT)

    TEST_USER_LIST = params['TEST_USER_LIST']
    for test in TEST_USER_LIST:
        if test[2] == False:
            push_cd_client(params, flag_curr_path_cd)
            result = start_vanessa(params, '@_' + test[0] + '.feature', True, test_name)
            test[2] = True
            if result == '2':
                test[3] = True



def env_prepare(params, DT):
    '''
    params - словарь параметров
    DT - ('role.dt') имя базы-эталона для данного тестирования
    *
    все действия подготовки к запуску тестов
    '''
    PREPARE_MODE = params['PREPARE_MODE']
    TEST_CATALOG = params['TEST_CATALOG']
    WORK_PATH = params['WORK_PATH']
    flag_curr_path_cd = ''

    #если нужно копировать ".cf" файл или обновляться из хранилища
    #т.е. если это первый тест в очереди 
    if PREPARE_MODE == 'cpcf' or PREPARE_MODE == 'uprep':
        del_path(TEST_CATALOG, params)
        prepare_st(params)
        sleep(1)
        create_base(params, 'manager')
        sleep(1)
        create_base(params, 'client', DT)
        sleep(1)
        eat_dt(params, 'manager')
        sleep(1)
        eat_dt(params, 'client')
        sleep(1)
        update_dt(params)
        sleep(1)
        reject_cd(params, DT)
        sleep(1)
        DT = ''
    #если это второй (и до конца) тест в очереди
    elif PREPARE_MODE == 'ret' or PREPARE_MODE == 'uprep+ret':
        if PREPARE_MODE == 'uprep+ret':
            prepare_st(params)
            sleep(1)
        flag_curr_path_cd = params['MODEL_ON_RUNNER'] + '\\' + 'storage_' + DT
        #если чистый, обновленный эталон не существует то создаем его
        #если существует возвращаем флаг с адресом директории
        if not path.isfile(flag_curr_path_cd + '\\1Cv8.1CD'):
            create_base(params, 'client', DT)
            sleep(1)
            eat_dt(params, 'manager')
            sleep(1)
            eat_dt(params, 'client')
            sleep(1)
            update_dt(params)
            sleep(1)
            reject_cd(params, DT)
            sleep(1)
            DT = ''
            flag_curr_path_cd = ''
    return flag_curr_path_cd



def end(client, servo):
    client.send('shutdown@none'.encode())
    client.close()
    servo.kill()



def main_func(sys_argv_list):
    '''
    MaiN
    получает лист со сценарием тестирования
    получает словарь с параметрами
    очищает тестовый каталог
    выполняет сценарии
    '''
    
    #proc('chcp 65001') #устанавливает кодировки в UTF для консоли
    proc('set PYTHONIOENCODING=utf-8')
    #proc('chcp 1251')
    #proc('set PYTHONIOENCODING=windows-1251')
    #print_cat()

    kill_1C()

    #получает все настройки и сценарий тестов
    params = ret_param_dict(sys_argv_list)
    scenario_list = params['SCEN']

    kill_python(params)

    #запускает отдельный процесс, следящий за выполнением консольных команд
    WORK_PATH = params['WORK_PATH']
    servo = start_servo(WORK_PATH, params['REPORTS_PATH'])
    log_save('SERVO PID : ' + str(servo.pid), params)
    client = start_client(servo)

    params['START_TIME'] = str(datetime.now())
    params['CLIENT'] = client
    
    #обходит каждый тест из сценария и выполняет его--------------------------------------------
    for test in scenario_list:
        #подготовка к запуску теста
        DT = test['DT']
        params['MODEL_ON_RUNNER_CURRENT_DT'] = params['MODEL_ON_RUNNER'] + DT
        params['MODEL_ADMIN_USER'] = test['ADM_USER']
        params['MODEL_USER'] = test['USER']
        params['PREPARE_MODE'] = test['PREPARE_MODE']

        flag_curr_path_cd = env_prepare(params, DT)

        TEST_FILE = test['TEST_FILE']
        ADD_HEAD = test['ADD_HEAD']
        ADD_TAIL = test['ADD_TAIL']
        ADDR = test["ADDR"]
        SWAP_CURR_STR = test["SWAP_CURR_STR"]

        #запуск тестов
        start_tests(params, TEST_FILE, ADD_HEAD, ADD_TAIL, flag_curr_path_cd, SWAP_CURR_STR, DT)
    #-------------------------------------------------------------------------------------------

    params['END_TIME'] = str(datetime.now())

    if len(sys_argv_list) <= 1:
        #запускает консольное меню с упавшими тестами, что бы воспроизвести их вновь----------------
        TEST_USER_LIST = params['TEST_USER_LIST']
        list_error_tests = []
        count = 0
        for i in TEST_USER_LIST:
            if i[3] == True:
                count = count + 1
                list_error_tests.append([str(count), i])

        flag_job_with_error_tests = True
        MODEL_ON_RUNNER = params['MODEL_ON_RUNNER']

        while flag_job_with_error_tests:
            #print_cat()
            print('start: {0}, end: {1}.'.format(params['START_TIME'], params['END_TIME']))
            for i in list_error_tests:
                print('{0}) {1}'.format(i[0], i[1][0]))
            print("\n$ введи номер теста для запуска,\n$ для выхода нажми \"0\",\n$ для отправки почты набери \"send\"")
            num = input('---------------------------> :')

            if num == '0':
                flag = False
                break

            elif num == 'send':
                #почтовая рассылка
                CONF_CURR = params["CONF"]
                err_list = open_file_r(WORK_PATH + 'log_spent_tests.txt')
                error_str = ''
                for i in err_list:
                    error_str = error_str + ''.join(i)
                for i in scenario_list:
                    ADDR = i['ADDR']
                    if ADDR != '':
                        try:
                            send_mail(dict(CONF = CONF_CURR, ADDR = ADDR, TEXT = error_str))
                        except:
                            log_save('ERROR send mail', params)

            else:
                for i in list_error_tests:
                    if i[0] == num:
                        test_name = i[1][0]
                        flag_curr_path_cd = MODEL_ON_RUNNER + '\\' + 'storage_' + i[1][4]
                        push_cd_client(params, flag_curr_path_cd)

                        params['FLAG_ERROR_START'] = True
                        params['ESC_VANESSA'] = 'Ложь'
                        params['ESC_TEST_CLIENT'] = 'Ложь'
                        start_vanessa(params, '@_' + test_name + '.feature', False, test_name)
        #-------------------------------------------------------------------------------------------

    end(client, servo)
    kill_python(params)



if __name__ == "__main__":
    main_func(sys.argv)