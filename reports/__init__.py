from .base_report import BaseReport, ReportFactory
from .students_performance import StudentPerformanceReport

ReportFactory.register("students_performance", StudentPerformanceReport)
