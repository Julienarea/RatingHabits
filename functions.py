# functions.py
import pytz
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

def is_habit_active(habit, today: date = None):
    """
    Проверяет, активна ли привычка на указанную дату.
    Если today не задан — использует текущую дату по ЕКБ.
    """
    if today is None:
        tz = pytz.timezone('Asia/Yekaterinburg')
        today = datetime.now(tz).date()

    # Парсим start_date
    if habit.start_date:
        try:
            start_date = datetime.strptime(habit.start_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            start_date = today
    else:
        start_date = today

    if today < start_date:
        return False

    repeat_type = habit.repeat_type or 'daily'
    repeat_every = int(habit.repeat_every) if habit.repeat_every and str(habit.repeat_every).isdigit() else 1

    if repeat_type == 'daily':
        days_passed = (today - start_date).days
        return days_passed >= 0 and days_passed % repeat_every == 0

    elif repeat_type == 'weekly':
        repeat_days = []
        if habit.repeat_days:
            for d in str(habit.repeat_days).split(','):
                d = d.strip()
                if d.isdigit():
                    day_int = int(d)
                    if 0 <= day_int <= 6:
                        repeat_days.append(day_int)
        if not repeat_days:
            repeat_days = list(range(7))

        if today.weekday() not in repeat_days:
            return False

        weeks_since_start = (today - start_date).days // 7
        return weeks_since_start % repeat_every == 0

    elif repeat_type == 'monthly':
        def get_effective_day(year, month, target_day):
            try:
                return date(year, month, target_day)
            except ValueError:
                return date(year, month, 1) + relativedelta(months=1) - relativedelta(days=1)

        effective_today = get_effective_day(today.year, today.month, start_date.day)
        if today != effective_today:
            return False

        months_passed = (today.year - start_date.year) * 12 + (today.month - start_date.month)
        return months_passed >= 0 and months_passed % repeat_every == 0

    elif repeat_type == 'yearly':
        if start_date.month == 2 and start_date.day == 29:
            if today.month == 2 and today.day == 28:
                if not (today.year % 4 == 0 and (today.year % 100 != 0 or today.year % 400 == 0)):
                    pass  # считаем 28.02 как 29.02
                else:
                    return False
            elif today.month == 2 and today.day == 29:
                pass
            else:
                return False
        else:
            if today.month != start_date.month or today.day != start_date.day:
                return False

        years_passed = today.year - start_date.year
        return years_passed >= 0 and years_passed % repeat_every == 0

    return False