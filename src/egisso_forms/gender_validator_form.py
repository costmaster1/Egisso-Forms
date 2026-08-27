from wtforms.validators import ValidationError

def gender_validator(form, field):
    data = field.data
    if not data:
        return
    # Приводим к верхнему регистру для сравнения
    data_upper = data.upper()
    if data_upper not in ('М', 'Ж'):
        raise ValidationError('Пол должен быть указан как "М" (мужской) или "Ж" (женский)')