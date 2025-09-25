from collections import defaultdict
from tabulate import tabulate

from .base_report import BaseReport


class TeacherPerformanceReport(BaseReport):
    """Отчет о средней оценке учеников у каждого учителя"""

    REQUIRED_FIELDS = ["teacher_name", "grade"]

    def validate_data(self) -> None:
        """Валидация данных"""
        required_fields = ["student_name", "grade"]
        for row in self.data:
            for field in required_fields:
                if field not in row:
                    raise ValueError(f"Поле {field} отсутствует в строке {row}")
                elif not row[field]:
                    raise ValueError(f"Поле {field} в строке {row} не может быть пустым")

    def calculate_teacher_performance(self) -> list:
        """Расчет средней оценки учеников у каждого учителя"""
        teacher_grades = defaultdict(lambda: {'grades': [], 'students': []})
        performance = []

        for row in self.data:
            try:
                t_name = row["teacher_name"]
                grade = float(row["grade"])
                student_name = row["student_name"]
                teacher_grades[t_name]["grades"].append(grade)
                teacher_grades[t_name]["students"].append(student_name)

            except (KeyError, ValueError) as e:
                if isinstance(e, KeyError):
                    print(f"Ошибка: отсутствует обязательное поле в строке {row}")
                else:
                    print(f"Неверный формат оценки в строке {row}: {e}")
                continue
        print(teacher_grades)

        for t_name, values in teacher_grades.items():
            if values["grades"]:
                avg_grade = sum(values["grades"]) / len(values["grades"])
                t_performance = {
                    "teacher_name": t_name,
                    "avg_grade": round(avg_grade, 2),
                    "students_count": len(values["students"]),
                    "students": sorted(list(values["students"])),
                }
                performance.append(t_performance)
        return sorted(performance, key=lambda x: x["avg_grade"], reverse=True)


    def generate(self) -> str:
        """Генерация отчета"""

        performance_data = self.calculate_teacher_performance()

        if not performance_data:
            raise ValueError("Нет данных для генерации отчета по учителям")

        headers = ["Учитель", "Средняя оценка", "Количество учеников", "Ученики"]

        table_data = [
            (item["teacher_name"], item["avg_grade"], item["students_count"], ', '.join(item["students"])) for item in performance_data
        ]
        return tabulate(table_data, headers=headers, tablefmt="simple_grid")