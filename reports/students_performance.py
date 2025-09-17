from .base_report import BaseReport
from tabulate import tabulate
from collections import defaultdict


class StudentPerformanceReport(BaseReport):
    """Отчет о среднем балле студентов"""

    def __init__(self, data):
        self.data = data
        self.validate_data()

    def validate_data(self):
        """Валидация данных"""
        required_fields = ["student_name", "grade"]
        for row in self.data:
            for field in required_fields:
                if field not in row:
                    raise ValueError(f"Поле {field} отсутствует в строке {row}")
                elif not row[field]:
                    raise ValueError(f"Поле {field} в строке {row} не может быть пустым")

    def calculate_performance(self):
        """Расчет среднего балла"""

        students_grades = defaultdict(list)
        performance = []

        for row in self.data:
            try:
                student_name = row["student_name"]
                grade = int(row["grade"])
                students_grades[student_name].append(grade)
            except (KeyError, ValueError) as e:
                if isinstance(e, KeyError):
                    print(f"Ошибка: {e}")
                else:
                    print(f"Неверный формат данных в строке {row}: {e}")
                continue

        for student_name, grades in students_grades.items():
            if grades:
                avg_grade = sum(grades) / len(grades)
                student_performance = {
                    "student_name": student_name,
                    "avg_grade": round(avg_grade, 1),
                }
                performance.append(student_performance)

        return sorted(performance, key=lambda x: x["avg_grade"], reverse=True)

    def generate(self):
        """Генерация отчета"""

        performance_data = self.calculate_performance()

        if not performance_data:
            raise ValueError("Нет данных для отчета")

        headers = ["Student Name", "Average Grade"]
        table_data = [(item["student_name"], item["avg_grade"]) for item in performance_data]

        return tabulate(table_data, headers=headers, tablefmt="grid")
