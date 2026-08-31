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

# Глобальные переменные для настроек (будут загружены из БД)
rectype = DEFAULT_SETTINGS['rectype']
assignmentfactuid = DEFAULT_SETTINGS['assignmentfactuid']
lmszid = DEFAULT_SETTINGS['lmszid']
categoryid = DEFAULT_SETTINGS['categoryid']
onmszcode = DEFAULT_SETTINGS['onmszcode']
lmszprovidercode = DEFAULT_SETTINGS['lmszprovidercode']
providercode = DEFAULT_SETTINGS['providercode']

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
        
        # Таблица пользователей
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
        
        # Таблица настроек
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Проверяем, есть ли настройки в БД, если нет - добавляем по умолчанию
        cursor.execute("SELECT COUNT(*) FROM settings")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Добавляем настройки по умолчанию
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
                    
                    # Используем загруженные настройки
                    values = [
                        rectype, assignmentfactuid, lmszid, categoryid, onmszcode, lmszprovidercode, providercode,
                        snils, family_name, name, patronymic, gender, 
                        birth_date.isoformat() if birth_date else '',
                        '', doc_series, doc_number, 
                        doc_issue_date.isoformat() if doc_issue_date else '',
                        doc_issuer,
                        '', '', '', '', '', '',
                        '', '', '', '', '', '',
                        '', '', '', '', '', '',
                        '', '', '', '', '', '', ''
                    ]
                    
                    # Проверяем количество значений
                    if len(values) != 43:
                        st.error(f"❌ Ошибка: ожидается 43 значения, получено {len(values)}")
                        return
                    
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


def show_settings():
    """Страница настроек приложения."""
    st.title("⚙️ Настройки ЕГИССО")
    st.caption("Управление системными настройками для полей RecType, assignmentFactUuid и др.")
    
    # Загружаем текущие настройки из БД
    try:
        conn = get_db()
        if conn is None:
            st.error("❌ Нет подключения к базе данных")
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT setting_key, setting_value, description FROM settings ORDER BY setting_key")
        settings_data = cursor.fetchall()
        conn.close()
        
        # Создаем словарь для удобства
        settings_dict = {row[0]: {'value': row[1], 'description': row[2]} for row in settings_data}
        
        # Отображаем форму настроек
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
            
            # Кнопки
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
                    # Сохраняем настройки
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
                        # Перезагружаем настройки
                        load_settings()
                        st.success("✅ Настройки успешно сохранены!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Ошибка при сохранении настроек")
            
            if reset:
                # Сбрасываем к значениям по умолчанию
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
        
        # Отображаем текущие значения
        st.divider()
        st.subheader("📊 Текущие значения настроек")
        
        # Показываем в виде таблицы
        settings_df = pd.DataFrame([
            {
                'Ключ': row[0],
                'Значение': row[1],
                'Описание': row[2]
            }
            for row in settings_data
        ])
        st.dataframe(settings_df, use_container_width=True, hide_index=True)
        
        # Показываем значения, которые используются сейчас
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
        
    except Exception as e:
        st.error(f"❌ Ошибка загрузки настроек: {str(e)}")


# ==================== ОСНОВНОЕ ПРИЛОЖЕНИЕ ====================

def main():
    """Главная функция приложения."""
    # Инициализация БД
    if not init_db():
        st.error("❌ Не удалось инициализировать базу данных")
        return
    
    # Загрузка настроек из БД
    load_settings()
    
    # Боковая панель навигации
    st.sidebar.title("📌 Навигация")
    
    if "page" not in st.session_state:
        st.session_state.page = "index"
    
    # Кнопки навигации
    if st.sidebar.button("📋 Главная", use_container_width=True):
        st.session_state.page = "index"
        st.rerun()
    
    if st.sidebar.button("📝 Новая запись", use_container_width=True):
        st.session_state.page = "register"
        st.rerun()
    
    st.sidebar.divider()
    st.sidebar.subheader("🔧 Администрирование")
    
    if st.sidebar.button("⚙️ Настройки", use_container_width=True):
        st.session_state.page = "settings"
        st.rerun()
    
    st.sidebar.divider()
    st.sidebar.info("📊 Версия 1.0.0")
    
    # Отображение выбранной страницы
    if st.session_state.page == "index":
        show_index()
    elif st.session_state.page == "register":
        show_register()
    elif st.session_state.page == "success":
        show_success()
    elif st.session_state.page == "settings":
        show_settings()
    else:
        show_index()


# ==================== ТОЧКА ВХОДА ====================

if __name__ == "__main__":
    main()
