from abc import ABC, abstractmethod
import csv


class BaseReport(ABC):
    """Базовый класс для отчетов."""

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
