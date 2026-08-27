import re
from wtforms.validators import ValidationError

def latin_name_validator(form, field):
    """
    Проверяет, что поле содержит только латинские буквы,
    первая буква заглавная, остальные строчные.
    Допускается дефис для двойных имён (опционально).
    """
    data = field.data
    if not data:  # пустое поле – пропускаем (для отчества)
        return
    
    # Проверка: только латинские буквы и опционально дефис
    if not re.fullmatch(r'[А-Яа-яЁё]+(-[А-Яа-яЁё]+)?', data):
     raise ValidationError('Используйте только кириллические буквы (А-Я, а-я, Ё, ё) и дефис (для двойных имён)')
    
    # Проверка первой буквы заглавной, остальные строчные
    if not (data[0].isupper() and data[1:].islower()):
        raise ValidationError('Первая буква должна быть заглавной, остальные — строчными')