import re
from wtforms.validators import ValidationError

def issuing_authority_validator(form, field):
    """
    Проверяет поле "Кем выдан паспорт" на допустимые символы и минимальную длину.
    Разрешены: кириллица (включая Ёё), цифры, пробелы, точки, дефисы, запятые, скобки.
    """
    data = field.data
    if not data:
        return

    # Минимальная длина – 5 символов (можно настроить)
    if len(data.strip()) < 5:
        raise ValidationError('Название органа, выдавшего паспорт, должно содержать не менее 5 символов')

    # Разрешённые символы: буквы кириллицы, цифры, пробелы, ., -, ,, (, )
    allowed_pattern = r'^[А-Яа-яЁё0-9\s\.\-–,()]+$'
    if not re.match(allowed_pattern, data):
        raise ValidationError('Допустимы только буквы кириллицы, цифры, пробелы, точки, дефисы, запятые и скобки')