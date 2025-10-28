import pytz
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

def is_habit_active(habit):
    tz = pytz.timezone('Asia/Yekaterinburg')
    today = datetime.now(tz).date()

    if habit.start_date:
        try:
            start_date = datetime.strptime(habit.start_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            start_date = today
    else:
        start_date = today

    if today < start_date:
        print(f"[DEBUG] Today {today} < start_date {start_date} → not active")
        return False

    repeat_type = habit.repeat_type or 'daily'
    repeat_every = int(habit.repeat_every) if habit.repeat_every and str(habit.repeat_every).isdigit() else 1

    if repeat_type == 'daily':
        days_passed = (today - start_date).days
        result = days_passed >= 0 and days_passed % repeat_every == 0
        print(f"[DEBUG] Daily: days_passed={days_passed}, repeat_every={repeat_every}, active={result}")
        return result

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
            print(f"[DEBUG] Weekly: today weekday={today.weekday()} not in {repeat_days} → not active")
            return False

        weeks_since_start = (today - start_date).days // 7
        result = weeks_since_start % repeat_every == 0
        print(f"[DEBUG] Weekly: weeks_since_start={weeks_since_start}, repeat_every={repeat_every}, active={result}")
        return result

    elif repeat_type == 'monthly':
        def get_effective_day(year, month, target_day):
            try:
                return date(year, month, target_day)
            except ValueError:
                return date(year, month, 1) + relativedelta(months=1) - relativedelta(days=1)

        effective_today = get_effective_day(today.year, today.month, start_date.day)
        if today != effective_today:
            print(f"[DEBUG] Monthly: today={today} != effective_day={effective_today} → not active")
            return False

        months_passed = (today.year - start_date.year) * 12 + (today.month - start_date.month)
        result = months_passed >= 0 and months_passed % repeat_every == 0
        print(f"[DEBUG] Monthly: months_passed={months_passed}, repeat_every={repeat_every}, active={result}")
        return result

    elif repeat_type == 'yearly':
        if start_date.month == 2 and start_date.day == 29:
            if today.month == 2 and today.day == 28:
                if not (today.year % 4 == 0 and (today.year % 100 != 0 or today.year % 400 == 0)):
                    effective_date = today
                else:
                    print("[DEBUG] Yearly: 28 Feb in leap year ≠ 29 Feb → not active")
                    return False
            elif today.month == 2 and today.day == 29:
                effective_date = today
            else:
                print("[DEBUG] Yearly: not Feb 28/29 → not active")
                return False
        else:
            if today.month != start_date.month or today.day != start_date.day:
                print(f"[DEBUG] Yearly: today={today} ≠ {start_date.month}-{start_date.day} → not active")
                return False
            effective_date = today

        years_passed = effective_date.year - start_date.year
        result = years_passed >= 0 and years_passed % repeat_every == 0
        print(f"[DEBUG] Yearly: years_passed={years_passed}, repeat_every={repeat_every}, active={result}")
        return result

    print(f"[DEBUG] Unknown repeat_type: {repeat_type} → not active")
    return False