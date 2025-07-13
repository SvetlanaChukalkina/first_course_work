import os

ROOT_DIR = os.path.dirname(__file__)
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
DATA_DIR = os.path.join(ROOT_DIR, 'data')
USER_SETTINGS = os.path.join(ROOT_DIR, 'user_settings.json')

PATH_JSON = ''
PATH_CSV = ''
PATH_XLSX = os.path.join(DATA_DIR, 'operations.xlsx')
PATH_LOGS = os.path.join(LOGS_DIR, 'logs.log')
