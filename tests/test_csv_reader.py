import sys

import pytest
import csv
import os
from unittest.mock import patch, mock_open

from reports import ReportFactory, StudentPerformanceReport
from reports.base_report import BaseReport


class TestBaseReport:
    """Тесты для базового класса отчетов"""

    def test_read_data_from_csv_valid_files(self, temp_csv_files, sample_student_data):
        """Тест чтения данных из валидных CSV файлов со всеми полями"""
        # print(f"Temp files: {temp_csv_files}")
        #
        # for file in temp_csv_files:
        #     print(f"Content of {file}:")
        #     with open(file, 'r') as f:
        #         content = f.read()
        #         print(content)
        #         print(f"Lines in {file}: {len(content.splitlines())}")
        data = BaseReport.read_data_from_csv(temp_csv_files)

        assert len(data) == len(sample_student_data)
        expected_fields = ['student_name', 'subject', 'teacher_name', 'date', 'grade']
        assert all(field in data[0] for field in expected_fields)
        # Проверяем, что оценки в правильном диапазоне
        grades = [int(row['grade']) for row in data if row['grade'].isdigit()]
        assert all(1 <= grade <= 5 for grade in grades)

    def test_read_data_from_csv_nonexistent_file(self, non_existent_file):
        """Тест чтения данных из несуществующего файла"""
        with pytest.raises(FileNotFoundError, match="Файл '/non/existent/file.csv' не найден"):
            BaseReport.read_data_from_csv([non_existent_file])

    def test_read_data_from_csv_empty_file(self, empty_csv_file):
        """Тест чтения данных из пустого CSV файла"""
        data = BaseReport.read_data_from_csv([empty_csv_file])
        assert len(data) == 0

    def test_read_data_from_multiple_files(self, temp_csv_files, sample_student_data):
        """Тест чтения данных из нескольких файлов"""
        data = BaseReport.read_data_from_csv(temp_csv_files)
        assert len(data) == len(sample_student_data)


class TestStudentPerformanceReport:
    """Тесты для отчета об успеваемости студентов"""

    REQUIRED_FIELDS = ["student_name", "grade"]
    ERROR_PATTERNS = {
        "missing": "отсутствует в строке",
        "empty": "не может быть пустым"
    }

    def test_validate_data_valid(self, sample_student_data):
        """Тест валидации корректных данных со всеми полями"""
        report = StudentPerformanceReport(sample_student_data)
        report.validate_data()  # Не должно вызывать исключение

    def test_validate_data_missing_required_field(self):
        """Тест валидации данных с отсутствующим обязательным полем"""
        invalid_data = [{'student_name': 'John Doe', 'subject': 'Math'}]  # Отсутствует поле grade

        with pytest.raises(ValueError, match="Поле grade отсутствует в строке"):
            report = StudentPerformanceReport(invalid_data)
            report.validate_data()

    @pytest.mark.parametrize("field, error_type", [
        (field, error_type)
        for field in REQUIRED_FIELDS
        for error_type in ["empty", "missing"]
    ])
    def test_validate_data_required_fields(self, field, error_type):
        """Комплексный тест валидации обязательных полей"""
        base_data = {
            'student_name': 'John Doe',
            'subject': 'Math',
            'teacher_name': 'Dr. Smith',
            'date': '2023-09-16',
            'grade': '5'
        }

        if error_type == "empty":
            test_data = base_data.copy()
            test_data[field] = ''
            expected_phrases = [f"Поле {field}", self.ERROR_PATTERNS[error_type]]
        else:  # missing
            test_data = base_data.copy()
            del test_data[field]
            expected_phrases = [f"Поле {field}", self.ERROR_PATTERNS[error_type]]

            # print("=== Тестовые данные ===")
            # print(test_data)
            # print("=== Ожидаемые фразы в ошибке ===")
            # print(expected_phrases)

        with pytest.raises(ValueError) as exc_info:
            report = StudentPerformanceReport([test_data])

        error_message = str(exc_info.value)
        # print("=== Сообщение об ошибке ===")
        # print(error_message)
        for phrase in expected_phrases:
            assert phrase in error_message, f"Ожидалась фраза '{phrase}' в ошибке: {error_message}"

    def test_calculate_performance_valid_data(self, sample_student_data):
        """Тест расчета успеваемости с валидными данными"""
        report = StudentPerformanceReport(sample_student_data)
        performance = report.calculate_performance()

        assert len(performance) > 0
        assert all('student_name' in item for item in performance)
        assert all('avg_grade' in item for item in performance)
        assert all(isinstance(item['avg_grade'], float) for item in performance)
        # Проверяем, что средние оценки в диапазоне 1-5
        assert all(1.0 <= item['avg_grade'] <= 5.0 for item in performance)

    def test_calculate_performance_invalid_grades_skipped(self):
        """Тест, что невалидные оценки пропускаются при расчете"""
        data = [
            {'student_name': 'John Doe', 'subject': 'Math', 'teacher_name': 'T1', 'date': '2023-09-16', 'grade': '5'},
            {'student_name': 'Jane Smith', 'subject': 'Science', 'teacher_name': 'T2', 'date': '2023-09-17',
             'grade': 'invalid'},
            {'student_name': 'Bob Johnson', 'subject': 'History', 'teacher_name': 'T3', 'date': '2023-09-18',
             'grade': '4'}
        ]

        report = StudentPerformanceReport(data)
        performance = report.calculate_performance()

        # Должны быть только студенты с валидными оценками
        assert len(performance) == 2
        student_names = [item['student_name'] for item in performance]

    def test_calculate_performance_multiple_grades_same_student(self):
        """Тест расчета средней оценки для студента с несколькими оценками"""
        data = [
            {'student_name': 'John Doe', 'subject': 'Math', 'teacher_name': 'T1', 'date': '2023-09-16', 'grade': '5'},
            {'student_name': 'John Doe', 'subject': 'Science', 'teacher_name': 'T2', 'date': '2023-09-17',
             'grade': '4'},
            {'student_name': 'John Doe', 'subject': 'History', 'teacher_name': 'T3', 'date': '2023-09-18', 'grade': '3'}
        ]

        report = StudentPerformanceReport(data)
        performance = report.calculate_performance()

        assert len(performance) == 1
        assert performance[0]['student_name'] == 'John Doe'
        assert performance[0]['avg_grade'] == 4.0  # (5+4+3)/3 = 4.0

    def test_generate_report_valid(self, sample_student_data):
        """Тест генерации отчета с валидными данными"""
        report = StudentPerformanceReport(sample_student_data)
        result = report.generate()

        # print("=== Отчет ===")
        # print(result)

        assert isinstance(result, str)
        assert "Student Name" in result
        assert "Average Grade" in result

    def test_generate_report_empty_data(self):
        """Тест генерации отчета с пустыми данными"""
        report = StudentPerformanceReport([])

        with pytest.raises(ValueError, match="Нет данных для отчета"):
            report.generate()

    def test_generate_report_sorted_descending(self, sample_student_data):
        """Тест сортировки отчета по убыванию средней оценки"""
        report = StudentPerformanceReport(sample_student_data)
        performance = report.calculate_performance()

        # Проверяем, что оценки отсортированы по убыванию
        grades = [item['avg_grade'] for item in performance]
        assert grades == sorted(grades, reverse=True)


class TestReportFactory:
    """Тесты для фабрики отчетов"""

    def test_create_existing_report(self, temp_csv_files):
        """Тест создания существующего отчета"""
        report = ReportFactory.create_report("students_performance", temp_csv_files)
        assert isinstance(report, StudentPerformanceReport)

    def test_create_nonexistent_report(self, temp_csv_files):
        """Тест создания несуществующего отчета"""
        with pytest.raises(ValueError, match=f"Отчет 'nonexistent' не зарегистрирован."):
            ReportFactory.create_report("nonexistent", temp_csv_files)

    def test_report_factory_registration(self):
        """Тест, что отчет зарегистрирован на фабрике"""
        assert "students_performance" in ReportFactory._reports
        assert ReportFactory._reports["students_performance"] == StudentPerformanceReport


class TestIntegration:
    """Интеграционные тесты полного workflow"""

    def test_end_to_end_workflow(self, temp_csv_files):
        """Тест полного workflow от чтения файлов до генерации отчета"""
        report = ReportFactory.create_report("students_performance", temp_csv_files)
        result = report.generate()

        assert isinstance(result, str)
        assert "Student Name" in result
        assert "Average Grade" in result

    def test_multiple_files_integration(self, temp_csv_files):
        """Тест обработки нескольких файлов"""
        data = BaseReport.read_data_from_csv(temp_csv_files)
        report = StudentPerformanceReport(data)
        performance = report.calculate_performance()

        assert len(performance) > 0
        # Все средние оценки должны быть в диапазоне 1-5
        assert all(1.0 <= item['avg_grade'] <= 5.0 for item in performance)

    def test_main_function_with_valid_args(self, capsys, temp_csv_files):
        """Тест основной функции с валидными аргументами"""
        # Добавляем путь к модулю для импорта
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

        # Создаем полный список аргументов
        args = ['main.py', '--files']
        args.extend(temp_csv_files)
        args.extend(['--report', 'students_performance'])

        with patch('sys.argv', args):
            from main import main
            main()

        captured = capsys.readouterr()
        assert "Student Name" in captured.out
        assert "Average Grade" in captured.out

    def test_main_function_with_nonexistent_file(self, capsys):
        """Тест основной функции с несуществующим файлом"""
        with patch('sys.argv', ['main.py', '--files', '/nonexistent/file.csv', '--report', 'students_performance']):
            from main import main
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_main_function_with_invalid_report(self, capsys, temp_csv_files):
        """Тест основной функции с невалидным типом отчета"""
        with patch('sys.argv', ['main.py', '--files', temp_csv_files[0], '--report', 'invalid_report']):
            from main import main
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        # print(captured.out)
        assert "Error" in captured.out
