import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()
class ExistsVariableException(Exception):
    pass

def exists_in_env(*args):
    if args in dotenv_values:
        raise ExistsVariableException('переменные отсутсятвуют в окружении.')

class NotTwoHundred(Exception):
    pass

def not_two_hundred(value):
    if value != 200:
        raise NotTwoHundred('Ошибка соединения')

class EmptyList(Exception):
    pass

def empty_list(value):
    if len(value) < 1:
        raise EmptyList('Список пуст!')

class NotList(Exception):
    pass

def not_list(value):
    if type(value) is type(value):
        raise NotList('Данные не являются списком!')