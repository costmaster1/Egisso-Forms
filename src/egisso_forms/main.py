import streamlit as st
import sqlite3
import os
from datetime import date
import pandas as pd

# Импортируем Flask для создания контекста
from flask import Flask, current_app

# Импортируем Flask-WTF формы и валидаторы
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired

# Импортируем существующие валидаторы
from snils_validator_form import snils_validator
from fio_validator_form import latin_name_validator
from gender_validator_form import gender_validator
from birthdate_recip_validator_form import validate_age
from series_pasport_validator_form import passport_series_validator
from namber_pasport_validator_form import passport_number_validator
from issuer_validator_form import issuing_authority_validator

# Импортируем настройки
from settings import rectype, assignmentfactuid, categoryid, lmszid, onmszcode, lmszprovidercode, providercode

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

# ==================== ФОРМА WTForms ====================

class Egisso_School(FlaskForm):
    """Класс формы с использованием WTForms валидаторов"""
    class Meta:
        csrf = False
    
    SNILS_recip = StringField('СНИЛС-Заявителя (родителя)', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        snils_validator
    ])

    FamilyName_recip = StringField('Фамилия-заявителя (родителя)', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        latin_name_validator
    ])

    Name_recip = StringField('Имя-заявителя (родителя)', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        latin_name_validator
    ])

    Patronymic_recip = StringField('Отчество-заявителя (родителя)', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        latin_name_validator
    ])

    Gender_recip = StringField('Пол-заявителя (родителя)', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        gender_validator
    ])

    BirthDate_recip = DateField('Дата рождения-заявителя (родителя)', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        validate_age
    ])

    doc_Series_recip = StringField('Серия паспорта-заявителя (родителя)', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        passport_series_validator
    ])

    doc_Number_recip = StringField('Номер паспорта-заявителя (родителя)', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        passport_number_validator
    ])

    doc_IssueDate_recip = DateField('Дата выдачи паспорта (родителя)', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        validate_age
    ])

    doc_Issuer_recip = StringField('Кем выдан паспорт (родителя)', validators=[
        DataRequired(message='Обязательное поле для ввода'),
        issuing_authority_validator
    ])
    
    submit = SubmitField('Отправить')


# ==================== ФУНКЦИИ ДЛЯ РАБОТЫ С БД ====================

def init_db():
    """Инициализирует базу данных."""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
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
            equivalentAmount TEXT NOT NULL
        )''')
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


# ==================== ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ВАЛИДАЦИИ ====================

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

def show_index():
    """Главная страница - просмотр записей."""
    st.title("📋 Реестр заявителей ЕГИССО")
    
    conn = get_db()
    if conn is None:
        st.error("❌ Нет подключения к базе данных")
        return
    
    try:
        df = pd.read_sql_query("SELECT * FROM users ORDER BY id DESC", conn)
        conn.close()
        
        if len(df) > 0:
            st.success(f"✅ Всего записей: {len(df)}")
            
            columns_to_show = ['id', 'SNILS_recip', 'FamilyName_recip', 'Name_recip', 
                              'Patronymic_recip', 'Gender_recip', 'BirthDate_recip']
            show_cols = [col for col in columns_to_show if col in df.columns]
            
            st.dataframe(df[show_cols], use_container_width=True)
            
            st.subheader("🔍 Детальный просмотр записи")
            ids = df['id'].tolist()
            if ids:
                selected_id = st.selectbox("Выберите ID для просмотра", ids)
                if selected_id:
                    record = df[df['id'] == selected_id].iloc[0]
                    st.json(record.to_dict())
        else:
            st.info("📭 Нет записей в базе данных")
    except Exception as e:
        st.error(f"❌ Ошибка при загрузке данных: {str(e)}")


def show_register():
    """Страница регистрации нового заявителя с использованием WTForms."""
    st.title("📝 Регистрация заявителя в ЕГИССО")
    
    with flask_app.app_context():
        form = Egisso_School()
    
    with st.form("register_form", clear_on_submit=False):
        st.header("👤 Данные заявителя (родителя)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            snils = st.text_input(
                "СНИЛС (родителя)*",
                value=form.SNILS_recip.data or "",
                placeholder="XXX-XXX-XXX YY",
                help="Формат: 123-456-789 01"
            )
            
            family_name = st.text_input(
                "Фамилия (родителя)*",
                value=form.FamilyName_recip.data or "",
                placeholder="Иванов",
                help="Только кириллица, первая буква заглавная"
            )
            
            name = st.text_input(
                "Имя (родителя)*",
                value=form.Name_recip.data or "",
                placeholder="Иван",
                help="Только кириллица, первая буква заглавная"
            )
            
            patronymic = st.text_input(
                "Отчество (родителя)*",
                value=form.Patronymic_recip.data or "",
                placeholder="Иванович",
                help="Только кириллица, первая буква заглавная"
            )
            
            gender = st.selectbox(
                "Пол (родителя)*",
                options=["", "М", "Ж"],
                index=0 if not form.Gender_recip.data else (1 if form.Gender_recip.data == "М" else 2),
                help="Выберите пол"
            )
        
        with col2:
            birth_date = st.date_input(
                "Дата рождения (родителя)*",
                value=form.BirthDate_recip.data or None,
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                help="Должно быть не менее 18 лет"
            )
            
            doc_series = st.text_input(
                "Серия паспорта (родителя)*",
                value=form.doc_Series_recip.data or "",
                placeholder="1234",
                help="Ровно 4 цифры"
            )
            
            doc_number = st.text_input(
                "Номер паспорта (родителя)*",
                value=form.doc_Number_recip.data or "",
                placeholder="123456",
                help="Ровно 6 цифр"
            )
            
            doc_issue_date = st.date_input(
                "Дата выдачи паспорта (родителя)*",
                value=form.doc_IssueDate_recip.data or None,
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                help="Дата выдачи паспорта"
            )
            
            doc_issuer = st.text_area(
                "Кем выдан паспорт (родителя)*",
                value=form.doc_Issuer_recip.data or "",
                placeholder="Отделом УФМС России по г. Москве",
                help="Не менее 5 символов"
            )
        
        st.divider()
        st.caption("Поля, отмеченные * обязательны для заполнения")
        
        submitted = st.form_submit_button("✅ Отправить", type="primary")
        
        if submitted:
            form.SNILS_recip.data = snils
            form.FamilyName_recip.data = family_name
            form.Name_recip.data = name
            form.Patronymic_recip.data = patronymic
            form.Gender_recip.data = gender
            form.BirthDate_recip.data = birth_date
            form.doc_Series_recip.data = doc_series
            form.doc_Number_recip.data = doc_number
            form.doc_IssueDate_recip.data = doc_issue_date
            form.doc_Issuer_recip.data = doc_issuer
            
            errors = []
            
            for field_name in ['SNILS_recip', 'FamilyName_recip', 'Name_recip', 
                              'Patronymic_recip', 'Gender_recip', 'BirthDate_recip',
                              'doc_Series_recip', 'doc_Number_recip', 
                              'doc_IssueDate_recip', 'doc_Issuer_recip']:
                valid, msg = validate_form_field(form, field_name)
                if not valid:
                    field_label = getattr(getattr(form, field_name), 'label', {}).text or field_name
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
                    # ПОДГОТОВКА 43 ЗНАЧЕНИЙ ДЛЯ INSERT
                    # ============================================================
                    values = [
                        # 1-7: Первые 7 полей (из settings.py)
                        rectype,           # 1  - RecType
                        assignmentfactuid, # 2  - assignmentFactUuid
                        lmszid,            # 3  - LMSZID
                        categoryid,        # 4  - categoryID
                        onmszcode,         # 5  - ONMSZCode
                        lmszprovidercode,  # 6  - LMSZProviderCode
                        providercode,      # 7  - providerCode
                        
                        # 8-18: Данные родителя (11 полей)
                        snils,                                          # 8  - SNILS_recip
                        family_name,                                    # 9  - FamilyName_recip
                        name,                                           # 10 - Name_recip
                        patronymic,                                     # 11 - Patronymic_recip
                        gender,                                         # 12 - Gender_recip
                        birth_date.isoformat() if birth_date else '',  # 13 - BirthDate_recip
                        '',                                             # 14 - doctype_recip
                        doc_series,                                     # 15 - doc_Series_recip
                        doc_number,                                     # 16 - doc_Number_recip
                        doc_issue_date.isoformat() if doc_issue_date else '',  # 17 - doc_IssueDate_recip
                        doc_issuer,                                     # 18 - doc_Issuer_recip
                        
                        # 19-25: Данные представителя (7 полей) - все пустые
                        '',  # 19 - SNILS_reason
                        '',  # 20 - FamilyName_reason
                        '',  # 21 - Name_reason
                        '',  # 22 - Patronymic_reason
                        '',  # 23 - Gender_reason
                        '',  # 24 - BirthDate_reason
                        
                        # 25: Степень родства
                        '',  # 25 - kinshipTypeCode
                        
                        # 26-30: Документы представителя (5 полей) - все пустые
                        '',  # 26 - doctype_reason
                        '',  # 27 - doc_Series_reason
                        '',  # 28 - doc_Number_reason
                        '',  # 29 - doc_IssueDate_reason
                        '',  # 30 - doc_Issuer_reason
                        
                        # 31-37: Остальные поля (7 полей) - все пустые
                        '',  # 31 - decision_date
                        '',  # 32 - dateStart
                        '',  # 33 - dateFinish
                        '',  # 34 - usingSign
                        '',  # 35 - criteria
                        '',  # 36 - criteriaCode
                        
                        # 37-43: Последние 7 полей
                        '',  # 37 - FormCode
                        '',  # 38 - amount
                        '',  # 39 - measuryCode
                        '',  # 40 - monetization
                        '',  # 41 - content
                        '',  # 42 - comment
                        ''   # 43 - equivalentAmount
                    ]
                    
                    # Проверяем количество значений
                    if len(values) != 43:
                        st.error(f"❌ Ошибка: ожидается 43 значения, получено {len(values)}")
                        return
                    
                    # Выполняем INSERT
                    cursor.execute('''INSERT INTO users (
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
                    
                    st.success("✅ Данные успешно добавлены!")
                    st.balloons()
                    
                    st.session_state.page = "success"
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Ошибка при сохранении: {str(e)}")

def show_success():
    """Страница успешной регистрации."""
    st.title("✅ Регистрация прошла успешно!")
    st.balloons()
    st.success("Данные заявителя успешно сохранены в системе ЕГИССО.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Перейти к списку записей", use_container_width=True):
            st.session_state.page = "index"
            st.rerun()
    with col2:
        if st.button("📝 Добавить новую запись", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()


# ==================== ОСНОВНОЕ ПРИЛОЖЕНИЕ ====================

def main():
    """Главная функция приложения."""
    if not init_db():
        st.error("❌ Не удалось инициализировать базу данных")
        return
    
    st.sidebar.title("📌 Навигация")
    
    if "page" not in st.session_state:
        st.session_state.page = "index"
    
    if st.sidebar.button("📋 Главная", use_container_width=True):
        st.session_state.page = "index"
        st.rerun()
    
    if st.sidebar.button("📝 Новая запись", use_container_width=True):
        st.session_state.page = "register"
        st.rerun()
    
    st.sidebar.divider()
    st.sidebar.info("📊 Версия 1.0.0")
    
    if st.session_state.page == "index":
        show_index()
    elif st.session_state.page == "register":
        show_register()
    elif st.session_state.page == "success":
        show_success()
    else:
        show_index()


# ==================== ТОЧКА ВХОДА ====================

if __name__ == "__main__":
    main()
