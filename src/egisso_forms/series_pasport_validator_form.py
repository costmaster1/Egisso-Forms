import re
from wtforms.validators import ValidationError

def passport_series_validator(form, field):
    """
    Проверяет, что поле содержит ровно 4 цифры.
    Допускается ввод с пробелом или дефисом (например, 1234 или 12 34 или 12-34).
    """
    data = field.data
    if not data:
        return

    # Удаляем всё, кроме цифр
    cleaned = re.sub(r'\D', '', data)

    if len(cleaned) != 4:
        raise ValidationError('Серия паспорта должна содержать ровно 4 цифры')

    # Опционально: проверка, что не все цифры нули
    if cleaned == '0000':
        raise ValidationError('Некорректная серия паспорта')