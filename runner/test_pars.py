# -*- coding: utf8 -*
#04mar20kg
#python 3.7.1

from re import split

from prepare import open_file_r, write_list_file, write_string_file
from log import log_save


'''
test_pars.py - подготавливает служебные тесты и конфиги, парсит тесты
'''



def va_params(param_dict, test_name):
    '''
    param_dict - словарь параметров
    test_name - имя теста, присваивается автоматически в зависимости от тэгов расставленых в фича-файле
    *
    собирает содержание json файла с настройками запуска теста для Ванессы
    нужно изменять крайне внимательно
    *
    return params - возвращает строку с содержанием файла
    '''
    TESTS_ON_RUNNER = param_dict['TESTS_ON_RUNNER']
    feature_path = TESTS_ON_RUNNER + test_name
    if test_name.find("@_") != -1:
        name = param_dict['CONF'] + '_' + split('[%.]', split('@_', test_name)[1])[0]
    else:
        name = param_dict['CONF'] + '_' + test_name

    feature_path = feature_path.replace('\\', '\\\\')
    platform = param_dict['PLATFORM_PATH_ON_RUNNER'].replace('\\', '\\\\')
    va = param_dict['VANESSA_ON_RUNNER'].replace('\\', '\\\\')
    tests = TESTS_ON_RUNNER.replace('\\', '\\\\')
    reports = param_dict['REPORTS_PATH'].replace('\\', '\\\\')

    params = '''{
	"Lang": "ru",
	"DebugLog": true,
	"КаталогФич": "''' + feature_path + '''",
	"ДобавлятьКИмениСценарияУсловияВыгрузки": false,
	"ИмяТекущейСборки": "''' + name + '''",
	"ЗагрузкаФичПриОткрытии": "Загружать",
	"ВерсияПлатформыДляГенерацииEPF": "''' + platform + '''\\\\bin",
        "ВыполнитьСценарии": true,
        "ЗавершитьРаботуСистемы": "''' + param_dict['ESC_VANESSA'] + '''",
        "ЗакрытьTestClientПослеЗапускаСценариев": "''' + param_dict['ESC_TEST_CLIENT'] + '''",
	"ВыполнениеСценариев": {
		"ВыполнятьШагиАссинхронно": false,
		"ИнтервалВыполненияШагаЗаданныйПользователем": 0.1,
		"ОбновлятьСтатистикуВДереве": true,
		"ОбновлятьДеревоПриНачалеВыполненияСценария": true,
		"ОстановкаПриВозникновенииОшибки": false,
		"ПоказыватьНомерСтрокиДереваПриВозникновенииОшибки": true,
		"ПриравниватьPendingКFailed": false,
		"ТаймаутДляАсинхронныхШагов": 0,
		"КоличествоСекундПоискаОкна": 5,
		"КоличествоПопытокВыполненияДействия": 3,
		"БезопасноеВыполнениеШагов": true,
		"ПаузаПриОткрытииОкна": 0
	},
	"КлиентТестирования": {
		"ЗапускатьКлиентТестированияСМаксимизированнымОкном": true,
		"ТаймаутЗапуска1С": 120,
		"ДиапазонПортовTestclient": "48100-48200",
		"ЗапускатьТестКлиентВРежимеОтладки": false,
		"КлючиОтладки": "",
		"АдресОтладчика": "",
		"ДанныеКлиентовТестирования": [
		]
	},
	"ДелатьОтчетВФорматеАллюр": "Истина",
	"КаталогOutputAllureБазовый": "''' + reports + '''",
	"СоздаватьПодкаталогВКаталогеAllureДляЭтойСборки": "Истина",
	"ДелатьОтчетВФорматеjUnit": false,
	"ДелатьОтчетВФорматеCucumberJson": false,
	"ДелатьОтчетВФорматеСППР": false,
	"СоздаватьИнструкциюHTML": false,
	"СоздаватьИнструкциюMarkdown": false,
	"ДелатьОтчетВоВнутреннемФормате": false,
	"КаталогиБиблиотек": "''' + va + '''features\\\Libraries",
	"ДелатьЛогВыполненияСценариевВЖР": true,
	"ДелатьЛогВыполненияСценариевВТекстовыйФайл": false,
	"ВыводитьВЛогВыполнениеШагов": false,
	"ДелатьЛогОшибокВТекстовыйФайл": false,
	"СобиратьДанныеОСостоянииАктивнойФормыПриОшибке": false,
	"СобиратьДанныеОСостоянииВсехФормПриОшибке": false,
	"ИмяФайлаЛогВыполненияСценариев": "''' + tests + test_name + '''",
	"ИмяКаталогаЛогОшибок": "''' + tests + '''",
	"КомандаСделатьСкриншот": "''' + '' + '''",
	"ДелатьСкриншотПриВозникновенииОшибки": false,
	"СниматьСкриншотКаждогоОкна1С": false,
	"КаталогПроекта": "''' + tests + '''",
	"СоздаватьИнструкциюВидео": false,
	"ИспользоватьSikuliXСервер": false,
	"ИскатьЭлементыФормыПоИмени": false,
	"ДобавлятьПриНакликиванииМетаИнформацию": false,
	"ТегTreeВключенПоУмолчанию": true
}
    '''
    log_save(params + '\n', param_dict)
    return params



def update_test(params, usr='adm'):
    '''
    params - словарь параметров
    usr - подставлять запуск от администратора или пользователя
    *
    собирает содержание файла с тестом: "Тест обновления программы"
    нужен для обновления эталонной базы
    *
    return test - возвращает строку с содержанием файла
    '''
    if usr == 'adm':
        user = params['MODEL_ADMIN_USER']
    elif usr == 'usr':
        user = params['MODEL_USER']
    else:
        user = ''

    test = '''#language: ru 
@tree
Функциональность: Тест обновления программы

Контекст: 
\tИ Я закрыл все окна клиентского приложения 

@КодСценария=000000001 
Сценарий: Тест обновления программы

\tКогда Я подключаю клиент тестирования с параметрами: 
\t\t| \'Имя\' | \'Синоним\' | \'Порт\' | \'Строка соединения\' | \'Логин\' | \'Пароль\' | \'Запускаемая обработка\' | \'Дополнительные параметры строки запуска\' |
\t\t| \'test\' | \'\' | \'\' | \'File="''' + params['WORK_PATH_BASE_CURR'] + '''";\' | \'''' + user + '''\' | \'\' | \'\' | \'\'|
\tКогда открылось окно \'Легальность получения обновлений\' 
\tИ я изменяю флаг \'Я подтверждаю легальность получения обновления в соответствии с вышеизложенными условиями\'
\tИ я нажимаю на кнопку \'Продолжить\'
\tИ я жду открытия окна "Что нового в конфигурации Розница, редакция 2.3" в течение 600 секунд
'''
    log_save(test + '\n', params)
    return test



def head_tail_test(what, params, name_list):
    '''
    what - cтрока определяет будет ли тест началом 'head' или концом 'tail'
    params - словарь параметров
    name - имя теста и имя пользователя
    *
    присоединяет шапку и сценарий запуска базы или присоединяет к концу сценарий закрытия базы
    *
    return list_str - возвращает строку сценария для добавления
    '''
    list_str = ''

    if what == 'head':
        list_str = '''#language: ru 
@tree
Функциональность: тест

Контекст: 
\tИ Я закрыл все окна клиентского приложения 

@КодСценария=000000666 
Сценарий: ''' + name_list[0] + '''

\tКогда Я подключаю клиент тестирования с параметрами: 
\t\t| \'Имя\' | \'Синоним\' | \'Порт\' | \'Строка соединения\' | \'Логин\' | \'Пароль\' | \'Запускаемая обработка\' | \'Дополнительные параметры строки запуска\' |
\t\t| \'test\' | \'\' | \'\' | \'File="''' + params['WORK_PATH_BASE_CURR'] + '''";\' | \'''' + name_list[1] + '''\' | \'\' | \'\' | \'\'|\n
'''
    elif what == 'tail':
        list_str = ''''''

    return list_str



def parse_dirty_test(file_list):
    '''
    file_list - список строк теста
    *
    по меткам "разрезает" на отдельные тесты
    метка #!$ - начало нового теста
    метка #$! - конец нового теста
    *
    return all_tests_list - возвращает список с тестами
    '''
    one_test_list = []
    one_test_list_append = one_test_list.append
    one_test_list_copy = one_test_list.copy
    one_test_list_clear = one_test_list.clear
    all_tests_list = []
    all_tests_list_append = all_tests_list.append
    flag = 0

    for i in file_list:
        if i.find("#!$") != -1:
            flag = 1
        elif i.find("#$!") != -1:
            flag = 2

        if flag == 1:
            one_test_list_append(i)
        elif flag == 2:
            current_test_list = one_test_list_copy()
            all_tests_list_append(current_test_list)
            one_test_list_clear()

    return all_tests_list



def write_curr_test(params, test, name_list, current_test_path, addit_strings_head='', addit_strings_tail=''):
    '''
    params - словарь параметров
    test - список, содержание теста
    name_list - имя теста и имя пользователя
    current_test_path - текущая директория + имя теста
    addit_strings_head - имя файла с тестом, тест прикрепляющийся к началу основного теста, если нужно
    addit_strings_tail - имя файла с тестом, тест прикрепляющийся к концу основного теста, если нужно
    *
    записывает текущий тест в файл
    '''
    test_path = params['TESTS_ON_RUNNER']
    #записали пустую строку создав файл
    write_string_file(current_test_path, 'w', '')

    if addit_strings_head != '':
        #записали "шаг" с запуском эталона
        write_string_file(current_test_path, 'w', head_tail_test('head', params, name_list))
        if addit_strings_head != 'only_start':
            #если перед тестом есть еще "шаги", получили и записали их
            list_addit_stings = open_file_r(test_path + '\\' + addit_strings_head + '.txt')
            write_list_file(list_addit_stings, current_test_path, 'a')

    #записали сам тест
    write_list_file(test, current_test_path, 'a')

    if addit_strings_tail != '':
        #получили и записали, если что то нужно добавить в хвост
        list_addit_stings = open_file_r(test_path + '\\' + addit_strings_tail + '.txt')
        write_list_file(list_addit_stings, current_test_path, 'a')



def prepare_tests(params, test_name, addit_strings_head='', addit_strings_tail='', SWAP_CURR_STR = [], DT=''):
    '''
    params - словарь параметров
    test_name - имя общего теста
    addit_strings_head - имя файла с тестом, тест прикрепляющийся к началу основного теста, если нужно
    addit_strings_tail - имя файла с тестом, тест прикрепляющийся к концу основного теста, если нужно
    *
    "режет" общий файл с тестом на N количество основных тестов для запуска
    прикрепляет к ним "голову" и "конец" если нужно
    '''
    test_path = params['TESTS_ON_RUNNER']
    USER = params['MODEL_USER']
    TEST_USER_LIST = params['TEST_USER_LIST']
    TEST_USER_LIST_append = TEST_USER_LIST.append

    test_list = open_file_r(test_path + '\\' + test_name)
    test_list = hot_swap(test_list, SWAP_CURR_STR, params['WORK_PATH_BASE_CURR'])
    all_tests = parse_dirty_test(test_list)

    for test in all_tests:
        if len(test) == 0:
            continue

        #извлекает имя пользователя из первой строки теста
        name_list = split('[$\n]', test[0])
        name = name_list[1]
        if USER == 'take_from_testname' or name.find("%") != -1:
            usr_list = split(r'[%.]', name)
            if len(usr_list) < 2:
                usr_name = ''
            else:
                usr_name = usr_list[1]
            curr_test_name = [name, usr_name, False, False, DT]
        else:
            curr_test_name = [name, USER, False, False, DT]

        #формирует имя файла с тестом
        current_test_path = '{0}\\@_{1}.feature'.format(test_path, name)
        log_save('директория текущего теста: ' + current_test_path + '\n', params)

        TEST_USER_LIST_append(curr_test_name)
        params['TEST_USER_LIST'] = TEST_USER_LIST

        write_curr_test(params, test, curr_test_name, current_test_path, addit_strings_head, addit_strings_tail)



def hot_swap(test_list, SWAP_CURR_STR, curr_client_dir):
    new_test_list = []
    new_test_list_append = new_test_list.append

    if len(SWAP_CURR_STR) != 0:
        for list_swap in SWAP_CURR_STR:
            if len(list_swap) == 2:
                swap_pattern = list_swap[0]
                swap_str = list_swap[1]

                for str_test in test_list:
                    if str_test.find(swap_pattern) != -1:
                        if swap_str == '@base_addr':
                            str_test = str_test.replace(swap_pattern, curr_client_dir)
                        else:
                            str_test = str_test.replace(swap_pattern, swap_str)
                    new_test_list_append(str_test)
    else:
        new_test_list = test_list
    return new_test_list



def print_cat():
    cat = '''\n
　　　　  　 ／＞　 フ
　　　 　　 | 　_　 _|
　  　　　 ／`ミ _x 彡
　 　 　 /　　　 　 |
 　　　 /　 ヽ　　 ﾉ
　／￣|　　 |　|　|
　| (￣ヽ＿_ヽ_)_)
　＼二つ
    \n'''
    print(cat)