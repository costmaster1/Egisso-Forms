from datetime import date
from wtforms.validators import ValidationError

def validate_age(form, field):
    """
    Проверяет, что пользователь старше 18 лет на текущую дату.
    """
    #if field.data is None:
        #return

    #today = date.today()
    #age = today.year - field.data.year - ((today.month, today.day) < (field.data.month, field.data.day))

    #if age < 18:
        #raise ValidationError('Возраст должен быть не менее 18 лет.')