import locale
from datetime import datetime

# Устанавливаем локаль на русский язык
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

def parse_review_date(date_str):
    current_year = datetime.now().year
    
    try:
        # Пробуем сначала интерпретировать строку как полный формат (ДД месяц ГГГГ)
        parsed_date = datetime.strptime(date_str, "%d %B %Y")
    except ValueError:
        try:
            # Если первый вариант не сработал, пробуем частичный формат (ДД месяц текущего года)
            parsed_date = datetime.strptime(f"{date_str} {current_year}", "%d %B %Y")
        except ValueError:
            raise ValueError("Невозможно распознать формат даты.")
        
    return parsed_date

# Пример использования
dates_to_test = ["24 апреля", "13 ноября 2024"]
for date in dates_to_test:
    print(parse_review_date(date))