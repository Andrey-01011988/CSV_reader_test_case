from .base_report import BaseReport, ReportFactory
from .students_performance import StudentPerformanceReport
from .teacher_performance import TeacherPerformanceReport

ReportFactory.register("students_performance", StudentPerformanceReport)
ReportFactory.register("teacher_performance",TeacherPerformanceReport)
