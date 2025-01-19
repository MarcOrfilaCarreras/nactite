import datetime


def get_months_in_year(year):
    result = []

    for month in range(1, 13):
        first_day = datetime.date(year, month, 1)

        if month == 12:
            last_day = datetime.date(year + 1, 1, 1) - \
                datetime.timedelta(days=1)
        else:
            last_day = datetime.date(
                year, month + 1, 1) - datetime.timedelta(days=1)

        month_name = first_day.strftime('%B')

        result.append({'name': month_name, 'first_day': first_day.strftime(
            '%Y-%m-%d'), 'last_day': last_day.strftime('%Y-%m-%d')})

    return result
