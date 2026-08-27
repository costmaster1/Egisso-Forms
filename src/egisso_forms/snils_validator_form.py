import re
from wtforms.validators import ValidationError

# ------------------------------------------------------------
# 1. Функция чистой проверки (без привязки к WTForms)
# ------------------------------------------------------------
def is_valid_snils(snils: str) -> bool:
    """
    Проверяет СНИЛС на корректность формата и контрольной суммы.
    Принимает строку в любом формате (с пробелами, дефисами или без).
    Возвращает True, если СНИЛС валидный.
    """
    # Удаляем всё, кроме цифр
    cleaned = re.sub(r'\D', '', snils)

    # Должно быть ровно 11 цифр
    if len(cleaned) != 11:
        return False

    # Проверка на спецслучай: номера 001-001-998 и ниже считаются некорректными
    # (по правилам ПФР, но это нестрогое требование, можно убрать)
    if int(cleaned[:9]) <= 1001998:
        return False

    # Разделяем на 9 цифр и контрольное число
    digits = [int(d) for d in cleaned[:9]]
    control = int(cleaned[-2:])

    # Расчёт контрольной суммы по алгоритму СНИЛС
    total = sum(d * (9 - i) for i, d in enumerate(digits))

    if total < 100:
        calculated = total
    elif total == 100 or total == 101:
        calculated = 0
    else:
        calculated = total % 101

    return calculated == control


# ------------------------------------------------------------
# 2. Валидатор для WTForms (выбрасывает ValidationError)
# ------------------------------------------------------------
def snils_validator(form, field):
    """
    Валидатор для использования в Flask-WTF форме.
    Пример: snils = StringField('СНИЛС', validators=[snils_validator])
    """
    if not field.data:
        return  # Пустое поле обрабатывается другим валидатором (DataRequired)

    if not is_valid_snils(field.data):
        raise ValidationError('Некорректный номер СНИЛС. Проверьте формат и контрольную сумму.')


# ------------------------------------------------------------
# 3. Опционально: валидатор с дополнительной проверкой формата
# ------------------------------------------------------------
def snils_validator_with_format(form, field):
    """
    Сначала проверяет формат "XXX-XXX-XXX YY", затем контрольную сумму.
    """
    if not field.data:
        return

    # Проверка формата
    if not re.fullmatch(r'\d{3}-\d{3}-\d{3} \d{2}', field.data):
        raise ValidationError('СНИЛС должен быть в формате XXX-XXX-XXX YY (например, 123-456-789 01)')

    # Проверка контрольной суммы
    if not is_valid_snils(field.data):
        raise ValidationError('Контрольная сумма СНИЛС не совпадает')