import argparse
import sys
from reports import ReportFactory


def main():
    parser = argparse.ArgumentParser(description='Генерация отчета')
    parser.add_argument("--files", nargs='+',required=True, help="Путь к файлам")
    parser.add_argument("--report", required=True, help="Выберите отчет:")

    args = parser.parse_args()

    try:
        report = ReportFactory.create_report(args.report, args.files)
        result = report.generate()
        print(result)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
