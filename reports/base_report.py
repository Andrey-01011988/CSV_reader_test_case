from abc import ABC, abstractmethod
import csv
from typing import List, Dict, Any


class BaseReport(ABC):
    """Базовый класс для отчетов."""
    REQUIRED_FIELDS: List[str] = []

    def __init__(self, data: List[Dict[str, Any]]) -> None:
        self.data = data
        self._validate_data()

    def _validate_data(self) -> None:
        """Общая валидация данных для всех отчетов"""
        if not self.REQUIRED_FIELDS:
            raise NotImplementedError("REQUIRED_FIELDS должен быть определен в дочернем классе")

        for i, row in enumerate(self.data):
            for field in self.REQUIRED_FIELDS:
                if field not in row:
                    raise ValueError(f"Поле '{field}' отсутствует в строке {i + 1}: {row}")
                elif not str(row[field]).strip():
                    raise ValueError(f"Поле '{field}' в строке {i + 1} не может быть пустым")

    @abstractmethod
    def generate(self):
        """Генерация отчета."""
        pass

    @classmethod
    def read_data_from_csv(cls, files):
        """Чтение данных из CSV файлов."""
        data = []
        for file in files:
            try:
                with open(file, 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    data.extend(list(reader))
            except FileNotFoundError:
                raise FileNotFoundError(f"Файл '{file}' не найден.")
            except csv.Error as e:
                raise csv.Error(f"Ошибка в файле '{file}': {e}") from e
            except Exception as e:
                raise Exception(f"Неизвестная ошибка при чтении файла '{file}': {e}") from e

        return data


class ReportFactory:
    """Фабрика отчетов."""

    _reports = {}

    @classmethod
    def register(cls, report_name, report_class):
        """Регистрация отчета."""
        cls._reports[report_name] = report_class

    @classmethod
    def create_report(cls, report_name, files):
        """Создание отчета."""
        if report_name not in cls._reports:
            raise ValueError(f"Отчет '{report_name}' не зарегистрирован.")

        report_class = cls._reports[report_name]
        data = report_class.read_data_from_csv(files)
        return report_class(data)
