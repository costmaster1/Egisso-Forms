import re
from wtforms.validators import ValidationError

def passport_number_validator(form, field):
    """
    Проверяет, что поле содержит ровно 6 цифр.
    Допускается ввод с пробелами или дефисами (очищаются).
    """
    data = field.data
    if not data:
        return

    # Удаляем все нецифровые символы
    cleaned = re.sub(r'\D', '', data)

    if len(cleaned) != 6:
        raise ValidationError('Номер паспорта должен содержать ровно 6 цифр')

    # Дополнительная проверка: номер не должен состоять из одних нулей
    if cleaned == '000000':
        raise ValidationError('Некорректный номер паспорта')