# settings.py
# Настройки по умолчанию для ЕГИССО

# Эти значения будут загружаться из БД при запуске
# Если в БД нет записей, используются значения по умолчанию

DEFAULT_SETTINGS = {
    'rectype': 'Fact',
    'assignmentfactuid': 'test',
    'lmszid': 'test',
    'categoryid': 'test',
    'onmszcode': 'test',
    'lmszprovidercode': 'test',
    'providercode': 'test'
}

# Эти переменные будут переопределены при загрузке из БД
rectype = DEFAULT_SETTINGS['rectype']
assignmentfactuid = DEFAULT_SETTINGS['assignmentfactuid']
lmszid = DEFAULT_SETTINGS['lmszid']
categoryid = DEFAULT_SETTINGS['categoryid']
onmszcode = DEFAULT_SETTINGS['onmszcode']
lmszprovidercode = DEFAULT_SETTINGS['lmszprovidercode']
providercode = DEFAULT_SETTINGS['providercode']
