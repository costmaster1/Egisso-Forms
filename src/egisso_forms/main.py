import streamlit as st
import sqlite3
import os
from datetime import date
import pandas as pd

# Импортируем Flask для создания контекста
from flask import Flask, current_app

# Импортируем Flask-WTF формы и валидаторы
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Optional

# Импортируем существующие валидаторы
from snils_validator_form import snils_validator
from fio_validator_form import latin_name_validator
from gender_validator_form import gender_validator
from birthdate_recip_validator_form import validate_age
from series_pasport_validator_form import passport_series_validator
from namber_pasport_validator_form import passport_number_validator
from issuer_validator_form import issuing_authority_validator

# Импортируем настройки по умолчанию
from settings import DEFAULT_SETTINGS

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================
st.set_page_config(
    page_title="ЕГИССО - Регистрация заявителей",
    page_icon="📋",
    layout="wide"
)

# ==================== СОЗДАЕМ КОНТЕКСТ FLASK ДЛЯ WTForms ====================
flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'ваш-секретный-ключ-здесь'
flask_app.config['WTF_CSRF_ENABLED'] = False

# ==================== НАСТРОЙКА БД ====================
DB_DIR = 'instance'
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DATABASE = os.path.join(DB_DIR, 'egisso.db')

# Глобальные переменные для настроек
rectype = DEFAULT_SETTINGS['rectype']
assignmentfactuid = DEFAULT_SETTINGS['assignmentfactuid']
lmszid = DEFAULT_SETTINGS['lmszid']
categoryid = DEFAULT_SETTINGS['categoryid']
onmszcode = DEFAULT_SETTINGS['onmszcode']
lmszprovidercode = DEFAULT_SETTINGS['lmszprovidercode']
providercode = DEFAULT_SETTINGS['providercode']

# ==================== ФОРМА WTForms ====================

class ChildCardForm(FlaskForm):
    """Форма для карточки ребенка (заявителя) - строго по шаблону"""
    class Meta:
        csrf = False
    
    # ===== ДАННЫЕ ПОЛУЧАТЕЛЯ (SNILS_recip) =====
    SNILS_recip = StringField('СНИЛС получателя', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        snils_validator
    ])
    
    FamilyName_recip = StringField('Фамилия получателя', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        latin_name_validator
    ])
    
    Name_recip = StringField('Имя получателя', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        latin_name_validator
    ])
    
    Patronymic_recip = StringField('Отчество получателя', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        latin_name_validator
    ])
    
    Gender_recip = SelectField('Пол получателя', choices=[
        ('', 'Выберите пол'),
        ('М', 'Мужской'),
        ('Ж', 'Женский')
    ], validators=[DataRequired(message='Обязательное поле для ввода')])
    
    BirthDate_recip = DateField('Дата рождения получателя', validators=[
        DataRequired(message='Обязательное поле для ввода')
    ])
    
    doctype_recip = SelectField('Тип документа получателя', choices=[
        ('', 'Выберите тип документа'),
        ('01', 'Паспорт гражданина РФ'),
        ('02', 'Загранпаспорт'),
        ('03', 'Свидетельство о рождении'),
        ('04', 'Другой документ')
    ], validators=[DataRequired(message='Обязательное поле для ввода')])
    
    doc_Series_recip = StringField('Серия документа получателя', validators=[
        DataRequired(message='Обязательное поле для ввода')
    ])
    
    doc_Number_recip = StringField('Номер документа получателя', validators=[
        DataRequired(message='Обязательное поле для ввода')
    ])
    
    doc_IssueDate_recip = DateField('Дата выдачи документа получателя', validators=[
        DataRequired(message='Обязательное поле для ввода')
    ])
    
    doc_Issuer_recip = TextAreaField('Кем выдан документ получателя', validators=[
        DataRequired(message='Обязательное поле для ввода')
    ])
    
    # ===== ДАННЫЕ ПРЕДСТАВИТЕЛЯ (reason) =====
    SNILS_reason = StringField('СНИЛС представителя', validators=[
        Optional(),
        snils_validator
    ])
    
    FamilyName_reason = StringField('Фамилия представителя', validators=[
        Optional(),
        latin_name_validator
    ])
    
    Name_reason = StringField('Имя представителя', validators=[
        Optional(),
        latin_name_validator
    ])
    
    Patronymic_reason = StringField('Отчество представителя', validators=[
        Optional(),
        latin_name_validator
    ])
    
    Gender_reason = SelectField('Пол представителя', choices=[
        ('', 'Выберите пол'),
        ('М', 'Мужской'),
        ('Ж', 'Женский')
    ], validators=[Optional()])
    
    BirthDate_reason = DateField('Дата рождения представителя', validators=[
        Optional()
    ])
    
    kinshipTypeCode = SelectField('Степень родства', choices=[
        ('', 'Выберите степень родства'),
        ('01', 'Родитель'),
        ('02', 'Опекун'),
        ('03', 'Попечитель'),
        ('04', 'Усыновитель'),
        ('05', 'Законный представитель')
    ], validators=[Optional()])
    
    doctype_reason = SelectField('Тип документа представителя', choices=[
        ('', 'Выберите тип документа'),
        ('01', 'Паспорт гражданина РФ'),
        ('02', 'Загранпаспорт'),
        ('03', 'Свидетельство о рождении'),
        ('04', 'Другой документ')
    ], validators=[Optional()])
    
    doc_Series_reason = StringField('Серия документа представителя', validators=[
        Optional()
    ])
    
    doc_Number_reason = StringField('Номер документа представителя', validators=[
        Optional()
    ])
    
    doc_IssueDate_reason = DateField('Дата выдачи документа представителя', validators=[
        Optional()
    ])
    
    doc_Issuer_reason = TextAreaField('Кем выдан документ представителя', validators=[
        Optional()
    ])
    
    # ===== ДОПОЛНИТЕЛЬНЫЕ ПАРАМЕТРЫ =====
    decision_date = DateField('Дата решения', validators=[Optional()])
    dateStart = DateField('Дата начала', validators=[Optional()])
    dateFinish = DateField('Дата окончания', validators=[Optional()])
    usingSign = SelectField('Признак использования', choices=[
        ('', 'Выберите'),
        ('Нет', 'Нет'),
        ('Да', 'Да')
    ], validators=[Optional()])
    criteria = StringField('Критерий', validators=[Optional()])
    criteriaCode = StringField('Код критерия', validators=[Optional()])
    FormCode = SelectField('Код формы', choices=[
        ('', 'Выберите'),
        ('01', 'Форма 01'),
        ('02', 'Форма 02'),
        ('03', 'Форма 03')
    ], validators=[Optional()])
    amount = StringField('Сумма', validators=[Optional()])
    measuryCode = SelectField('Код измерения', choices=[
        ('', 'Выберите'),
        ('01', 'Рубли'),
        ('02', 'Проценты')
    ], validators=[Optional()])
    monetization = SelectField('Монетизация', choices=[
        ('', 'Выберите'),
        ('Нет', 'Нет'),
        ('Да', 'Да')
    ], validators=[Optional()])
    content = TextAreaField('Содержание', validators=[Optional()])
    comment = TextAreaField('Комментарий', validators=[Optional()])
    equivalentAmount = StringField('Эквивалентная сумма', validators=[Optional()])
    
    submit = SubmitField('Сохранить запись')


# ==================== ФУНКЦИИ ДЛЯ РАБОТЫ С БД ====================

def init_db():
    """Инициализирует базу данных СТРОГО ПО ШАБЛОНУ."""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # ============================================================
        # ТАБЛИЦА children - СТРОГО ПО ШАБЛОНУ (43 колонки)
        # ============================================================
        cursor.execute('''CREATE TABLE IF NOT EXISTS children (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            RecType TEXT NOT NULL,
            assignmentFactUuid TEXT NOT NULL,
            LMSZID TEXT NOT NULL,
            categoryID TEXT NOT NULL,
            ONMSZCode TEXT NOT NULL,
            LMSZProviderCode TEXT NOT NULL,
            providerCode TEXT NOT NULL,
            SNILS_recip TEXT NOT NULL,
            FamilyName_recip TEXT NOT NULL,
            Name_recip TEXT NOT NULL,
            Patronymic_recip TEXT NOT NULL,
            Gender_recip TEXT NOT NULL,
            BirthDate_recip TEXT NOT NULL,
            doctype_recip TEXT NOT NULL,
            doc_Series_recip TEXT NOT NULL,
            doc_Number_recip TEXT NOT NULL,
            doc_IssueDate_recip TEXT NOT NULL,
            doc_Issuer_recip TEXT NOT NULL,
            SNILS_reason TEXT NOT NULL,
            FamilyName_reason TEXT NOT NULL,
            Name_reason TEXT NOT NULL,
            Patronymic_reason TEXT NOT NULL,
            Gender_reason TEXT NOT NULL,
            BirthDate_reason TEXT NOT NULL,
            kinshipTypeCode TEXT NOT NULL,
            doctype_reason TEXT NOT NULL,
            doc_Series_reason TEXT NOT NULL,
            doc_Number_reason TEXT NOT NULL,
            doc_IssueDate_reason TEXT NOT NULL,
            doc_Issuer_reason TEXT NOT NULL,
            decision_date TEXT NOT NULL,
            dateStart TEXT NOT NULL,
            dateFinish TEXT NOT NULL,
            usingSign TEXT NOT NULL,
            criteria TEXT NOT NULL,
            criteriaCode TEXT NOT NULL,
            FormCode TEXT NOT NULL,
            amount TEXT NOT NULL,
            measuryCode TEXT NOT NULL,
            monetization TEXT NOT NULL,
            content TEXT NOT NULL,
            comment TEXT NOT NULL,
            equivalentAmount TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # ============================================================
        # ТАБЛИЦА settings - для настроек администратора
        # ============================================================
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Добавляем настройки по умолчанию
        cursor.execute("SELECT COUNT(*) FROM settings")
        count = cursor.fetchone()[0]
        
        if count == 0:
            default_settings = [
                ('rectype', DEFAULT_SETTINGS['rectype'], 'Тип записи'),
                ('assignmentfactuid', DEFAULT_SETTINGS['assignmentfactuid'], 'UUID назначения'),
                ('lmszid', DEFAULT_SETTINGS['lmszid'], 'ID ЛМСЗ'),
                ('categoryid', DEFAULT_SETTINGS['categoryid'], 'ID категории'),
                ('onmszcode', DEFAULT_SETTINGS['onmszcode'], 'Код ОНМСЗ'),
                ('lmszprovidercode', DEFAULT_SETTINGS['lmszprovidercode'], 'Код поставщика ЛМСЗ'),
                ('providercode', DEFAULT_SETTINGS['providercode'], 'Код поставщика')
            ]
            cursor.executemany(
                "INSERT INTO settings (setting_key, setting_value, description) VALUES (?, ?, ?)",
                default_settings
            )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Ошибка при инициализации БД: {str(e)}")
        return False


def get_db():
    """Возвращает соединение с БД."""
    try:
        return sqlite3.connect(DATABASE)
    except Exception as e:
        st.error(f"❌ Ошибка подключения к БД: {str(e)}")
        return None


def load_settings():
    """Загружает настройки из БД в глобальные переменные."""
    global rectype, assignmentfactuid, lmszid, categoryid, onmszcode, lmszprovidercode, providercode
    
    try:
        conn = get_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        cursor.execute("SELECT setting_key, setting_value FROM settings")
        rows = cursor.fetchall()
        conn.close()
        
        for key, value in rows:
            if key == 'rectype':
                rectype = value
            elif key == 'assignmentfactuid':
                assignmentfactuid = value
            elif key == 'lmszid':
                lmszid = value
            elif key == 'categoryid':
                categoryid = value
            elif key == 'onmszcode':
                onmszcode = value
            elif key == 'lmszprovidercode':
                lmszprovidercode = value
            elif key == 'providercode':
                providercode = value
        
        return True
    except Exception as e:
        st.error(f"❌ Ошибка загрузки настроек: {str(e)}")
        return False


def save_settings_to_db(settings_dict):
    """Сохраняет настройки в БД."""
    try:
        conn = get_db()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        for key, value in settings_dict.items():
            cursor.execute(
                "UPDATE settings SET setting_value = ?, updated_at = CURRENT_TIMESTAMP WHERE setting_key = ?",
                (value, key)
            )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Ошибка сохранения настроек: {str(e)}")
        return False


def validate_form_field_with_context(form, field_name):
    """Валидация поля формы WTForms в контексте Flask приложения"""
    field = getattr(form, field_name)
    try:
        with flask_app.app_context():
            for validator in field.validators:
                validator(form, field)
        return True, ""
    except Exception as e:
        return False, str(e)


def validate_form_field(form, field_name):
    """Валидация поля формы WTForms (обертка)"""
    return validate_form_field_with_context(form, field_name)


# ==================== СТРАНИЦЫ ПРИЛОЖЕНИЯ ====================

def show_add_record():
    """Страница добавления новой записи - СТРОГО ПО ШАБЛОНУ"""
    st.title("📝 Добавление новой записи")
    st.caption("Заполните все поля для создания записи в системе ЕГИССО (строго по шаблону)")
    
    with flask_app.app_context():
        form = ChildCardForm()
    
    with st.form("add_record_form", clear_on_submit=False):
        # ===== БЛОК 1: ДАННЫЕ ПОЛУЧАТЕЛЯ =====
        st.header("👤 Данные получателя (SNILS_recip)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            snils_recip = st.text_input(
                "СНИЛС получателя*",
                value=form.SNILS_recip.data or "",
                placeholder="XXX-XXX-XXX YY",
                help="Формат: 123-456-789 01"
            )
            
            family_name_recip = st.text_input(
                "Фамилия получателя*",
                value=form.FamilyName_recip.data or "",
                placeholder="Петрова"
            )
            
            name_recip = st.text_input(
                "Имя получателя*",
                value=form.Name_recip.data or "",
                placeholder="Анна"
            )
            
            patronymic_recip = st.text_input(
                "Отчество получателя*",
                value=form.Patronymic_recip.data or "",
                placeholder="Васильевна"
            )
            
            gender_recip = st.selectbox(
                "Пол получателя*",
                options=["", "М", "Ж"],
                index=0 if not form.Gender_recip.data else (1 if form.Gender_recip.data == "М" else 2)
            )
        
        with col2:
            birth_date_recip = st.date_input(
                "Дата рождения получателя*",
                value=form.BirthDate_recip.data or None,
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )
            
            doctype_recip = st.selectbox(
                "Тип документа получателя*",
                options=["", "01", "02", "03", "04"],
                format_func=lambda x: {
                    "": "Выберите тип документа",
                    "01": "Паспорт гражданина РФ",
                    "02": "Загранпаспорт",
                    "03": "Свидетельство о рождении",
                    "04": "Другой документ"
                }.get(x, x)
            )
            
            doc_series_recip = st.text_input(
                "Серия документа получателя*",
                value=form.doc_Series_recip.data or "",
                placeholder="1317"
            )
            
            doc_number_recip = st.text_input(
                "Номер документа получателя*",
                value=form.doc_Number_recip.data or "",
                placeholder="578098"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            doc_issue_date_recip = st.date_input(
                "Дата выдачи документа получателя*",
                value=form.doc_IssueDate_recip.data or None,
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )
        
        with col4:
            doc_issuer_recip = st.text_area(
                "Кем выдан документ получателя*",
                value=form.doc_Issuer_recip.data or "",
                placeholder="УМВД РОССИИ ПО АРХАНГЕЛЬСКОЙ ОБЛАСТИ"
            )
        
        # ===== БЛОК 2: ДАННЫЕ ПРЕДСТАВИТЕЛЯ =====
        st.divider()
        st.header("👥 Данные представителя (SNILS_reason)")
        
        col5, col6 = st.columns(2)
        
        with col5:
            snils_reason = st.text_input(
                "СНИЛС представителя",
                value=form.SNILS_reason.data or "",
                placeholder="XXX-XXX-XXX YY"
            )
            
            family_name_reason = st.text_input(
                "Фамилия представителя",
                value=form.FamilyName_reason.data or "",
                placeholder="Иванова"
            )
            
            name_reason = st.text_input(
                "Имя представителя",
                value=form.Name_reason.data or "",
                placeholder="Мария"
            )
            
            patronymic_reason = st.text_input(
                "Отчество представителя",
                value=form.Patronymic_reason.data or "",
                placeholder="Петровна"
            )
        
        with col6:
            gender_reason = st.selectbox(
                "Пол представителя",
                options=["", "М", "Ж"],
                index=0 if not form.Gender_reason.data else (1 if form.Gender_reason.data == "М" else 2)
            )
            
            birth_date_reason = st.date_input(
                "Дата рождения представителя",
                value=form.BirthDate_reason.data or None,
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )
            
            kinship_type_code = st.selectbox(
                "Степень родства",
                options=["", "01", "02", "03", "04", "05"],
                format_func=lambda x: {
                    "": "Выберите степень родства",
                    "01": "Родитель",
                    "02": "Опекун",
                    "03": "Попечитель",
                    "04": "Усыновитель",
                    "05": "Законный представитель"
                }.get(x, x)
            )
        
        st.divider()
        st.subheader("📄 Документы представителя")
        
        col7, col8 = st.columns(2)
        
        with col7:
            doctype_reason = st.selectbox(
                "Тип документа представителя",
                options=["", "01", "02", "03", "04"],
                format_func=lambda x: {
                    "": "Выберите тип документа",
                    "01": "Паспорт гражданина РФ",
                    "02": "Загранпаспорт",
                    "03": "Свидетельство о рождении",
                    "04": "Другой документ"
                }.get(x, x)
            )
            
            doc_series_reason = st.text_input(
                "Серия документа представителя",
                value=form.doc_Series_reason.data or "",
                placeholder="1234"
            )
            
            doc_number_reason = st.text_input(
                "Номер документа представителя",
                value=form.doc_Number_reason.data or "",
                placeholder="123456"
            )
        
        with col8:
            doc_issue_date_reason = st.date_input(
                "Дата выдачи документа представителя",
                value=form.doc_IssueDate_reason.data or None,
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )
            
            doc_issuer_reason = st.text_area(
                "Кем выдан документ представителя",
                value=form.doc_Issuer_reason.data or "",
                placeholder="Отделом УФМС России по г. Москве"
            )
        
        # ===== БЛОК 3: ДОПОЛНИТЕЛЬНЫЕ ПАРАМЕТРЫ =====
        st.divider()
        st.header("📊 Дополнительные параметры")
        
        col9, col10 = st.columns(2)
        
        with col9:
            decision_date = st.date_input(
                "Дата решения",
                value=form.decision_date.data or None,
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )
            
            date_start = st.date_input(
                "Дата начала",
                value=form.dateStart.data or None,
                min_value=date(1900, 1, 1)
            )
            
            date_finish = st.date_input(
                "Дата окончания",
                value=form.dateFinish.data or None,
                min_value=date(1900, 1, 1)
            )
            
            using_sign = st.selectbox(
                "Признак использования",
                options=["", "Нет", "Да"],
                index=0 if not form.usingSign.data else (1 if form.usingSign.data == "Нет" else 2)
            )
            
            criteria = st.text_input(
                "Критерий",
                value=form.criteria.data or "",
                placeholder="Критерий"
            )
            
            criteria_code = st.text_input(
                "Код критерия",
                value=form.criteriaCode.data or "",
                placeholder="Код критерия"
            )
        
        with col10:
            form_code = st.selectbox(
                "Код формы",
                options=["", "01", "02", "03"],
                format_func=lambda x: {
                    "": "Выберите",
                    "01": "Форма 01",
                    "02": "Форма 02",
                    "03": "Форма 03"
                }.get(x, x)
            )
            
            amount = st.text_input(
                "Сумма",
                value=form.amount.data or "",
                placeholder="15000"
            )
            
            measury_code = st.selectbox(
                "Код измерения",
                options=["", "01", "02"],
                format_func=lambda x: {
                    "": "Выберите",
                    "01": "Рубли",
                    "02": "Проценты"
                }.get(x, x)
            )
            
            monetization = st.selectbox(
                "Монетизация",
                options=["", "Нет", "Да"],
                index=0 if not form.monetization.data else (1 if form.monetization.data == "Нет" else 2)
            )
        
        content = st.text_area(
            "Содержание",
            value=form.content.data or "",
            placeholder="Описание содержания..."
        )
        
        comment = st.text_area(
            "Комментарий",
            value=form.comment.data or "",
            placeholder="Дополнительный комментарий..."
        )
        
        equivalent_amount = st.text_input(
            "Эквивалентная сумма",
            value=form.equivalentAmount.data or "",
            placeholder="0"
        )
        
        st.divider()
        st.caption("Поля, отмеченные * обязательны для заполнения")
        
        submitted = st.form_submit_button("💾 Сохранить запись", type="primary")
        
        if submitted:
            # Заполняем форму данными
            form.SNILS_recip.data = snils_recip
            form.FamilyName_recip.data = family_name_recip
            form.Name_recip.data = name_recip
            form.Patronymic_recip.data = patronymic_recip
            form.Gender_recip.data = gender_recip
            form.BirthDate_recip.data = birth_date_recip
            form.doctype_recip.data = doctype_recip
            form.doc_Series_recip.data = doc_series_recip
            form.doc_Number_recip.data = doc_number_recip
            form.doc_IssueDate_recip.data = doc_issue_date_recip
            form.doc_Issuer_recip.data = doc_issuer_recip
            
            form.SNILS_reason.data = snils_reason
            form.FamilyName_reason.data = family_name_reason
            form.Name_reason.data = name_reason
            form.Patronymic_reason.data = patronymic_reason
            form.Gender_reason.data = gender_reason
            form.BirthDate_reason.data = birth_date_reason
            form.kinshipTypeCode.data = kinship_type_code
            form.doctype_reason.data = doctype_reason
            form.doc_Series_reason.data = doc_series_reason
            form.doc_Number_reason.data = doc_number_reason
            form.doc_IssueDate_reason.data = doc_issue_date_reason
            form.doc_Issuer_reason.data = doc_issuer_reason
            
            form.decision_date.data = decision_date
            form.dateStart.data = date_start
            form.dateFinish.data = date_finish
            form.usingSign.data = using_sign
            form.criteria.data = criteria
            form.criteriaCode.data = criteria_code
            form.FormCode.data = form_code
            form.amount.data = amount
            form.measuryCode.data = measury_code
            form.monetization.data = monetization
            form.content.data = content
            form.comment.data = comment
            form.equivalentAmount.data = equivalent_amount
            
            errors = []
            required_fields = [
                ('SNILS_recip', 'СНИЛС получателя'),
                ('FamilyName_recip', 'Фамилия получателя'),
                ('Name_recip', 'Имя получателя'),
                ('Patronymic_recip', 'Отчество получателя'),
                ('Gender_recip', 'Пол получателя'),
                ('BirthDate_recip', 'Дата рождения получателя'),
                ('doctype_recip', 'Тип документа получателя'),
                ('doc_Series_recip', 'Серия документа получателя'),
                ('doc_Number_recip', 'Номер документа получателя'),
                ('doc_IssueDate_recip', 'Дата выдачи документа получателя'),
                ('doc_Issuer_recip', 'Кем выдан документ получателя')
            ]
            
            for field_name, field_label in required_fields:
                valid, msg = validate_form_field(form, field_name)
                if not valid:
                    errors.append(f"{field_label}: {msg}")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    conn = get_db()
                    if conn is None:
                        st.error("❌ Нет подключения к базе данных")
                        return
                    
                    cursor = conn.cursor()
                    
                    # ============================================================
                    # ПОДГОТОВКА 43 ЗНАЧЕНИЙ ДЛЯ INSERT - СТРОГО ПО ШАБЛОНУ
                    # ============================================================
                    values = [
                        # 1-7: Системные поля (из настроек)
                        rectype,                                        # 1  - RecType
                        assignmentfactuid,                              # 2  - assignmentFactUuid
                        lmszid,                                         # 3  - LMSZID
                        categoryid,                                     # 4  - categoryID
                        onmszcode,                                      # 5  - ONMSZCode
                        lmszprovidercode,                               # 6  - LMSZProviderCode
                        providercode,                                   # 7  - providerCode
                        
                        # 8-18: Данные получателя (SNILS_recip)
                        snils_recip,                                    # 8  - SNILS_recip
                        family_name_recip,                              # 9  - FamilyName_recip
                        name_recip,                                     # 10 - Name_recip
                        patronymic_recip,                               # 11 - Patronymic_recip
                        gender_recip,                                   # 12 - Gender_recip
                        birth_date_recip.isoformat() if birth_date_recip else '',  # 13 - BirthDate_recip
                        doctype_recip if doctype_recip else '',         # 14 - doctype_recip
                        doc_series_recip,                               # 15 - doc_Series_recip
                        doc_number_recip,                               # 16 - doc_Number_recip
                        doc_issue_date_recip.isoformat() if doc_issue_date_recip else '',  # 17 - doc_IssueDate_recip
                        doc_issuer_recip,                               # 18 - doc_Issuer_recip
                        
                        # 19-25: Данные представителя (SNILS_reason)
                        snils_reason if snils_reason else '',           # 19 - SNILS_reason
                        family_name_reason if family_name_reason else '',  # 20 - FamilyName_reason
                        name_reason if name_reason else '',             # 21 - Name_reason
                        patronymic_reason if patronymic_reason else '', # 22 - Patronymic_reason
                        gender_reason if gender_reason else '',         # 23 - Gender_reason
                        birth_date_reason.isoformat() if birth_date_reason else '',  # 24 - BirthDate_reason
                        kinship_type_code if kinship_type_code else '', # 25 - kinshipTypeCode
                        
                        # 26-30: Документы представителя
                        doctype_reason if doctype_reason else '',       # 26 - doctype_reason
                        doc_series_reason if doc_series_reason else '', # 27 - doc_Series_reason
                        doc_number_reason if doc_number_reason else '', # 28 - doc_Number_reason
                        doc_issue_date_reason.isoformat() if doc_issue_date_reason else '',  # 29 - doc_IssueDate_reason
                        doc_issuer_reason if doc_issuer_reason else '', # 30 - doc_Issuer_reason
                        
                        # 31-43: Дополнительные параметры
                        decision_date.isoformat() if decision_date else '',  # 31 - decision_date
                        date_start.isoformat() if date_start else '',   # 32 - dateStart
                        date_finish.isoformat() if date_finish else '', # 33 - dateFinish
                        using_sign if using_sign else '',               # 34 - usingSign
                        criteria if criteria else '',                   # 35 - criteria
                        criteria_code if criteria_code else '',         # 36 - criteriaCode
                        form_code if form_code else '',                 # 37 - FormCode
                        amount if amount else '',                       # 38 - amount
                        measury_code if measury_code else '',           # 39 - measuryCode
                        monetization if monetization else '',           # 40 - monetization
                        content if content else '',                     # 41 - content
                        comment if comment else '',                     # 42 - comment
                        equivalent_amount if equivalent_amount else ''  # 43 - equivalentAmount
                    ]
                    
                    # Проверяем количество значений
                    if len(values) != 43:
                        st.error(f"❌ Ошибка: ожидается 43 значения, получено {len(values)}")
                        return
                    
                    # ============================================================
                    # INSERT СТРОГО ПО ШАБЛОНУ (43 колонки)
                    # ============================================================
                    cursor.execute('''INSERT INTO children (
                        RecType, assignmentFactUuid, LMSZID, categoryID, ONMSZCode, LMSZProviderCode, providerCode,
                        SNILS_recip, FamilyName_recip, Name_recip, Patronymic_recip, Gender_recip, BirthDate_recip,
                        doctype_recip, doc_Series_recip, doc_Number_recip, doc_IssueDate_recip, doc_Issuer_recip,
                        SNILS_reason, FamilyName_reason, Name_reason, Patronymic_reason, Gender_reason, BirthDate_reason,
                        kinshipTypeCode, doctype_reason, doc_Series_reason, doc_Number_reason, doc_IssueDate_reason,
                        doc_Issuer_reason, decision_date, dateStart, dateFinish, usingSign, criteria, criteriaCode,
                        FormCode, amount, measuryCode, monetization, content, comment, equivalentAmount
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', values)
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("✅ Запись успешно сохранена!")
                    st.balloons()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Ошибка при сохранении: {str(e)}")


def show_records():
    """Страница просмотра всех записей"""
    st.title("📋 Список записей")
    st.caption("Просмотр всех сохраненных записей (строго по шаблону)")
    
    conn = get_db()
    if conn is None:
        st.error("❌ Нет подключения к базе данных")
        return
    
    try:
        df = pd.read_sql_query("SELECT * FROM children ORDER BY id DESC", conn)
        conn.close()
        
        if len(df) > 0:
            st.success(f"✅ Всего записей: {len(df)}")
            
            # Показываем таблицу с основными данными
            columns_to_show = ['id', 'SNILS_recip', 'FamilyName_recip', 'Name_recip', 
                              'Patronymic_recip', 'Gender_recip', 'BirthDate_recip']
            show_cols = [col for col in columns_to_show if col in df.columns]
            st.dataframe(df[show_cols], use_container_width=True)
            
            # Детальный просмотр
            st.subheader("🔍 Детальный просмотр записи")
            ids = df['id'].tolist()
            if ids:
                selected_id = st.selectbox("Выберите ID для просмотра", ids)
                if selected_id:
                    record = df[df['id'] == selected_id].iloc[0]
                    st.json(record.to_dict())
            
            # Экспорт в CSV
            st.divider()
            st.subheader("📥 Экспорт данных")
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Скачать CSV",
                data=csv,
                file_name=f"egisso_records_{date.today().isoformat()}.csv",
                mime="text/csv"
            )
        else:
            st.info("📭 Нет записей в базе данных")
    except Exception as e:
        st.error(f"❌ Ошибка при загрузке данных: {str(e)}")


def show_settings():
    """Страница настроек администратора"""
    st.title("⚙️ Настройки системы")
    st.caption("Управление системными параметрами ЕГИССО")
    
    # Загружаем текущие настройки
    conn = get_db()
    if conn is None:
        st.error("❌ Нет подключения к базе данных")
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT setting_key, setting_value, description FROM settings ORDER BY setting_key")
    settings_data = cursor.fetchall()
    conn.close()
    
    settings_dict = {row[0]: {'value': row[1], 'description': row[2]} for row in settings_data}
    
    # Создаем вкладки внутри настроек
    tab1, tab2 = st.tabs(["📝 Редактирование", "📊 Просмотр"])
    
    with tab1:
        with st.form("settings_form"):
            st.subheader("📝 Основные настройки")
            st.info("Эти значения будут использоваться при создании новых записей")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_rectype = st.text_input(
                    "RecType (Тип записи)",
                    value=settings_dict.get('rectype', {}).get('value', ''),
                    help="Тип записи, по умолчанию 'Fact'"
                )
                
                new_assignmentfactuid = st.text_input(
                    "assignmentFactUuid (UUID назначения)",
                    value=settings_dict.get('assignmentfactuid', {}).get('value', ''),
                    help="UUID назначения факта"
                )
                
                new_lmszid = st.text_input(
                    "LMSZID (ID ЛМСЗ)",
                    value=settings_dict.get('lmszid', {}).get('value', ''),
                    help="Идентификатор ЛМСЗ"
                )
                
                new_categoryid = st.text_input(
                    "categoryID (ID категории)",
                    value=settings_dict.get('categoryid', {}).get('value', ''),
                    help="Идентификатор категории"
                )
            
            with col2:
                new_onmszcode = st.text_input(
                    "ONMSZCode (Код ОНМСЗ)",
                    value=settings_dict.get('onmszcode', {}).get('value', ''),
                    help="Код ОНМСЗ"
                )
                
                new_lmszprovidercode = st.text_input(
                    "LMSZProviderCode (Код поставщика ЛМСЗ)",
                    value=settings_dict.get('lmszprovidercode', {}).get('value', ''),
                    help="Код поставщика ЛМСЗ"
                )
                
                new_providercode = st.text_input(
                    "providerCode (Код поставщика)",
                    value=settings_dict.get('providercode', {}).get('value', ''),
                    help="Код поставщика"
                )
            
            st.divider()
            st.caption("Все поля обязательны для заполнения")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button("💾 Сохранить настройки", type="primary", use_container_width=True)
            with col_btn2:
                reset = st.form_submit_button("🔄 Сбросить к значениям по умолчанию", use_container_width=True)
            
            if submitted:
                if not all([new_rectype, new_assignmentfactuid, new_lmszid, new_categoryid, 
                           new_onmszcode, new_lmszprovidercode, new_providercode]):
                    st.error("❌ Все поля должны быть заполнены!")
                else:
                    settings_to_save = {
                        'rectype': new_rectype,
                        'assignmentfactuid': new_assignmentfactuid,
                        'lmszid': new_lmszid,
                        'categoryid': new_categoryid,
                        'onmszcode': new_onmszcode,
                        'lmszprovidercode': new_lmszprovidercode,
                        'providercode': new_providercode
                    }
                    
                    if save_settings_to_db(settings_to_save):
                        load_settings()
                        st.success("✅ Настройки успешно сохранены!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Ошибка при сохранении настроек")
            
            if reset:
                settings_to_save = {
                    'rectype': DEFAULT_SETTINGS['rectype'],
                    'assignmentfactuid': DEFAULT_SETTINGS['assignmentfactuid'],
                    'lmszid': DEFAULT_SETTINGS['lmszid'],
                    'categoryid': DEFAULT_SETTINGS['categoryid'],
                    'onmszcode': DEFAULT_SETTINGS['onmszcode'],
                    'lmszprovidercode': DEFAULT_SETTINGS['lmszprovidercode'],
                    'providercode': DEFAULT_SETTINGS['providercode']
                }
                
                if save_settings_to_db(settings_to_save):
                    load_settings()
                    st.success("🔄 Настройки сброшены к значениям по умолчанию!")
                    st.rerun()
                else:
                    st.error("❌ Ошибка при сбросе настроек")
    
    with tab2:
        st.subheader("📊 Текущие значения настроек")
        
        settings_df = pd.DataFrame([
            {
                'Ключ': row[0],
                'Значение': row[1],
                'Описание': row[2]
            }
            for row in settings_data
        ])
        st.dataframe(settings_df, use_container_width=True, hide_index=True)
        
        st.subheader("🔧 Активные настройки")
        st.json({
            'rectype': rectype,
            'assignmentfactuid': assignmentfactuid,
            'lmszid': lmszid,
            'categoryid': categoryid,
            'onmszcode': onmszcode,
            'lmszprovidercode': lmszprovidercode,
            'providercode': providercode
        })


# ==================== ОСНОВНОЕ ПРИЛОЖЕНИЕ ====================

def main():
    """Главная функция приложения."""
    # Инициализация БД
    if not init_db():
        st.error("❌ Не удалось инициализировать базу данных")
        return
    
    # Загрузка настроек
    load_settings()
    
    # Заголовок приложения
    st.sidebar.title("📌 ЕГИССО")
    st.sidebar.markdown("---")
    
    # Навигация по вкладкам
    page = st.sidebar.radio(
        "Выберите раздел:",
        ["📝 Добавление новой записи", "📋 Список записей", "⚙️ Настройки"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("📊 Версия 2.0.0")
    st.sidebar.caption("Система регистрации заявителей")
    st.sidebar.caption("БД строго по шаблону (43 колонки)")
    
    # Отображение выбранной страницы
    if page == "📝 Добавление новой записи":
        show_add_record()
    elif page == "📋 Список записей":
        show_records()
    elif page == "⚙️ Настройки":
        show_settings()


# ==================== ТОЧКА ВХОДА ====================

if __name__ == "__main__":
    main()
