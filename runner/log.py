# -*- coding: utf8 -*
#04mar20kg
#python 3.7.1

import logging
from datetime import datetime



def log_save(str_log, params):
    '''
    '''
    log_path = '{0}\\main_log_({1}).log'.format(params['REPORTS_PATH'], params['CONF'])
    logging.basicConfig(filename=log_path, level=logging.DEBUG)

    final_str = '\n' + str(datetime.now()) + ': *** ' + str_log + ' ***\n'

    logging.debug(final_str)
    print(final_str)
