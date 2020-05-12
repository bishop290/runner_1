# -*- coding: utf8 -*
#04mar20kg
#python 3.7.1
#psutil 5.4.8

import subprocess
import socket
from multiprocessing import Process
from time import sleep
import psutil
from os import path


'''
proc.py - работа с процессами
'''



def write_string_file(filename, wr_str, cur_dir):
    '''
    filename - полный путь с именем до файла
    wr_str - строка которую записываем в файл
    *
    записывает строку в файл на компьютере
    '''
    if path.isfile(filename):
        param_write = 'a'
    else:
        if not path.exists(cur_dir):
            mkdir(cur_dir)
        param_write = 'w'
    with open(filename, param_write, encoding="utf8") as my_file:
        my_file.write(wr_str)
    my_file.close()



def kill_1C():
    '''
    name_pr - строка с именем
    *
    убивает все процессы(+дочерние) с определенным именем
    '''
    try:
        for p in psutil.process_iter():
            try:
                p_name = p.name()
                if p_name == '1cv8.exe' or p_name == '1cv8c.exe':
                    print("! kill: " + p_name + '\n')
                    proc("Taskkill /IM " + p_name + " /F")
            except:
                pass
    except:
        print('ERROR kill proc\n')



def kill_python(params):
    '''
    '''
    curr_pid = int(params['PID'])
    try:
        for p in psutil.process_iter():
            try:
                p_name = p.name()
                p_pid = p.pid
                if p_name == 'python.exe':
                    if p_pid != curr_pid:
                        print("! kill: " + p_name + '\n')
                        proc("Taskkill /PID " + p_pid)
            except:
                pass
    except:
        print('ERROR kill proc\n')    



def open_file_r(filename, enc="windows-1251"):
    '''
    filename - полный путь с именем до файла
    *
    читает файл на компьютере
    *
    return file_list - возвращает список с прочитанными строками
    '''
    file_list = []
    file_list_append = file_list.append
    try:
        with open(filename, "r", encoding=enc) as my_file:
            for line in my_file:
                file_list_append(line)
        my_file.close()
    except IOError:
        my_file.close()

    return file_list



def search_pid(curr_pid, work_dir, final_log_dir, kill_all = False):
    '''
    curr_pid - номер процесса

    kill_all - флаг, True убивает все процессы 1С при завершении
    *
    если в текущих процессах есть процесс то ждем секунду и снова проверяем то же самое
    если прождали 1200 секунд (20 минут) то убиваем процесс
    '''
    count = 0
    flag_proc_exist = False #флаг указывает на то что процесс существует
    test_name = ''
    count_int = 2000 #сколько итераций ожидать процесс (каждая чуть больше секунды)
    ret_send_val = '0' # 1 - ошибок не было, 2 - была ошибка в тесте, 0 - неопределено

    while count <= count_int:
        #ПРОВЕРКА СУЩЕСТВОВАНИЯ ПРОЦЕССА
        for proc in psutil.process_iter():
            try:
                if proc.pid == curr_pid:
                    flag_proc_exist = True
                    break
            except:
                pass
        #-----------------------------------------------------

        #ПОПЫТКА ПРОВЕРИТЬ ЛОГ ВАНЕССЫ НА ЗАВЕРШЕННОСТЬ ЗАДАЧИ
        if kill_all:
                vanessa_log_dir = work_dir + 'log.txt'
                if path.exists(vanessa_log_dir):
                    log_list = open_file_r(vanessa_log_dir)
                    if len(log_list) != 0:
                        for log_str in reversed(log_list):
                            if log_str.find('Работаю по сценарию:') != -1:
                                test_name = log_str

                            if log_str.find('Ошибок не было') != -1:
                                #отмечаем что тест был пройден
                                ret_send_val = '1'

                                flag_proc_exist = False
                                final_str = '{0}{1}\n'.format(test_name, log_str)
                                write_string_file(final_log_dir + '\\log_spent_tests.txt', final_str, final_log_dir)
                                test_name = ''
                                error_info = ''
                                break
                            elif log_str.find('ОписаниеОшибки') != -1:
                                error_info = log_str
                            elif log_str.find('БЫЛИ ОШИБКИ') != -1:
                                #отмечаем что тест был пройден, добавляем текущий тест в ошибки
                                ret_send_val = '2'

                                flag_proc_exist = False
                                final_str = '{0}{1}{2}\n'.format(test_name, error_info, log_str)
                                write_string_file(final_log_dir + '\\log_spent_tests.txt', final_str, final_log_dir)
                                test_name = ''
                                error_info = ''
                                break
        #-----------------------------------------------------

        if flag_proc_exist == False:
            break
        count = count + 1
        flag_proc_exist = False
        sleep(1)

    #если тест завис и прошло count_int итераций то записываем тест как завершившийся с ошибкой.
    if kill_all and count == count_int:
        ret_send_val = '2'

    if kill_all:
        sleep(1)
        kill_1C()

    return ret_send_val



def wait_1c(p_1c, work_dir, final_log_dir, kill_all=False):
    '''
    p_1c - строка, имя процесса 1с, который нужно отследить ('1cv8.exe' - конфигуратор, '1cv8c.exe' - режим предприятия)
    work_dir
    final_log_dir
    kill_all - флаг, True убивает все процессы 1С при завершении
    *
    нужна, что бы определить главный процесс, что бы ждать именно его (менеджер, а не клиент тестирования)
    из всех процессов выбирает все совпадающие с именем аргумента функции,
    сортирует их по времени создания,
    за текущий процесс считает последний созданный на момент выборки.
    ждет его исполнения около 20 минут
    '''
    p_1c_list = []
    for proc in psutil.process_iter():
        try:
            if proc.name() == p_1c:
                p_1c_list.append(
                        {'pid' : proc.pid, 'time_start' : proc.create_time()})
        except:
            pass

    if len(p_1c_list) == 0:
        ret_send_val = '0'
    else:
        sort_p_1c_list = sorted(p_1c_list, key=lambda x: x['time_start'])
        [print(i) for i in sort_p_1c_list]
        curr_pid = sort_p_1c_list[-1]['pid']
        ret_send_val = search_pid(curr_pid, work_dir, final_log_dir, kill_all)
    return ret_send_val



def proc_prior(proc, p_class):
    '''
    proc -  процесса
    p_class - "H"(высокий) или "R"(реального времени) класс процесса
    *
    назначает процессам приоритет
    '''
    try:
        for p in psutil.process_iter():
            try:
                if p.name() == proc:
                    if p_class == 'H':
                        p.nice(psutil.HIGH_PRIORITY_CLASS)
                    elif p_class == 'R':
                        p.nice(psutil.REALTIME_PRIORITY_CLASS)
            except:
                pass
    except:
        print('ERROR ' + p_class + ' class \n')



def servo(work_dir, final_log_dir):
    def inner_cicle(data_list, kill):
        ret_send_val = '0'
        count = 0
        flag = False
        name_proc = data_list[1]

        while count <= 1200:
            for p in psutil.process_iter():
                try:
                    if p.name() == name_proc:
                        flag = True

                        #что бы после запуска ванессы получал приоритет клиент
                        if name_proc == '1cv8.exe' and kill == True:
                            proc_prior('1cv8c.exe','H')
                        else:
                            proc_prior(name_proc,'H')
                        #----------------------------------------------------

                        ret_send_val = wait_1c(name_proc, work_dir, final_log_dir, kill)
                        break
                except:
                    pass
            if flag:
                break
            else:
                count = count + 1
        return ret_send_val


    sock = socket.socket()
    sock.bind(('localhost', 9080))
    sock.listen(1)
    conn, addr = sock.accept()

    while True:
        try:
            data = conn.recv(1024)
            data = data.decode()
        except:
            data = '@'

            sock = socket.socket()
            sock.bind(('localhost', 9080))
            sock.listen(1)
            conn, addr = sock.accept()

        data_list = data.split('@')

        if len(data_list) == 2:
            command_to_servo = data_list[0]
            if command_to_servo == 'wait':
                ret_send_val = inner_cicle(data_list, False)
                conn.send(ret_send_val.encode())
            elif command_to_servo == 'wait_and_kill':
                ret_send_val = inner_cicle(data_list, True)
                conn.send(ret_send_val.encode())
            elif command_to_servo == 'shutdown':
                conn.send("1".encode())
                conn.close()
                sock.close()
            else:
                conn.send("0".encode())
        sleep(1)


def dif_proc(func, args_list):
    p = Process(target=func, args=args_list)
    p.start()
    return p


def start_servo(work_dir, final_log_dir):
    return dif_proc(servo, [work_dir, final_log_dir])



def start_client(servo):
    sock = socket.socket()
    try:
        sock.connect(('localhost', 9080))
    except:
        print('ERROR sock.connect\n')
        sock.close()
        servo.kill()
        exit()
    return sock



def proc(command, p_1c='', kill_all=False, sock=None):
    '''
    command - принимает строку консольной команды.
    p_1c - строка, имя процесса, который нужно ждать.
    kill_all - флаг, True убивает все процессы 1С при завершении
    *
    запускает и ожидает завершение процесса.
    '''
    process = subprocess.Popen(command, shell=True)
    sleep(5)

    if p_1c != '' and sock !=  None:
        if kill_all:
            str_comm = 'wait_and_kill@' + p_1c
            sock.send(str_comm.encode())
        else:
            str_comm = 'wait@' + p_1c
            sock.send(str_comm.encode())

    process.communicate()

    data = '0'
    if p_1c != '' and sock !=  None:
        data = sock.recv(1024)
        data = data.decode()

    return data
