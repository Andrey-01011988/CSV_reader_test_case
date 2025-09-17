import pytest
import csv
import tempfile
import os
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()


@pytest.fixture
def sample_student_data():
    """Фикстура для создания тестовых данных студентов"""
    data = []
    for _ in range(15):
        data.append({
            'student_name': fake.name(),
            'subject': fake.random_element(['Math', 'Science', 'History', 'Literature', 'Physics']),
            'teacher_name': fake.name(),
            'date': (datetime.now() - timedelta(days=fake.random_int(1, 30))).strftime('%Y-%m-%d'),
            'grade': str(fake.random_int(1, 5))  # Оценки от 1 до 5
        })
    return data


@pytest.fixture
def temp_csv_files(sample_student_data):
    """Фикстура для создания временных CSV файлов со всеми полями"""
    temp_files = []

    # Создаем несколько временных файлов
    for i in range(2):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=[
                'student_name', 'subject', 'teacher_name', 'date', 'grade'
            ])
            writer.writeheader()
            # Разделяем данные между файлами
            start_idx = i * 8
            end_idx = start_idx + 8
            writer.writerows(sample_student_data[start_idx:end_idx])
            temp_files.append(f.name)

    yield temp_files

    # Удаляем временные файлы после тестов
    for file in temp_files:
        if os.path.exists(file):
            os.unlink(file)


@pytest.fixture
def invalid_csv_file():
    """Фикстура для создания CSV файла с невалидными данными"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=[
            'student_name', 'subject', 'teacher_name', 'date', 'grade'
        ])
        writer.writeheader()
        writer.writerow({
            'student_name': 'John Doe',
            'subject': 'Math',
            'teacher_name': 'Dr. Smith',
            'date': '2023-09-16',
            'grade': ''  # Пустое поле grade
        })
        writer.writerow({
            'student_name': '',  # Пустое поле student_name
            'subject': 'Science',
            'teacher_name': 'Dr. Brown',
            'date': '2023-09-17',
            'grade': '5'
        })
        writer.writerow({
            'student_name': 'Jane Smith',
            'subject': 'History',
            'teacher_name': 'Dr. Wilson',
            'date': '2023-09-18',
            'grade': 'invalid'  # Невалидная оценка
        })

    yield f.name

    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def empty_csv_file():
    """Фикстура для создания пустого CSV файла"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=[
            'student_name', 'subject', 'teacher_name', 'date', 'grade'
        ])
        writer.writeheader()

    yield f.name

    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def non_existent_file():
    """Фикстура возвращает путь к несуществующему файлу"""
    return "/non/existent/file.csv"
