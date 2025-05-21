from datetime import datetime, date, timedelta
from dateutil import parser
from typing import Union

class DateUtils:
    @staticmethod
    def to_datetime(value: Union[str, int, float, datetime, date]) -> datetime:
        if isinstance(value, datetime):
            return value
        elif isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        elif isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        elif isinstance(value, str):
            return parser.parse(value)
        else:
            raise ValueError(f"Tipo non supportato: {type(value)}")

    @staticmethod
    def compare_dates(date1, date2, truncate_to_day=True) -> int:
        dt1 = DateUtils.to_datetime(date1)
        dt2 = DateUtils.to_datetime(date2)

        if truncate_to_day:
            dt1 = dt1.date()
            dt2 = dt2.date()

        if dt1 < dt2:
            return -1
        elif dt1 > dt2:
            return 1
        else:
            return 0

    @staticmethod
    def is_today(value) -> bool:
        dt = DateUtils.to_datetime(value).date()
        return dt == date.today()

    @staticmethod
    def is_between(target, start, end, inclusive=True) -> bool:
        dt = DateUtils.to_datetime(target)
        start_dt = DateUtils.to_datetime(start)
        end_dt = DateUtils.to_datetime(end)

        if inclusive:
            return start_dt <= dt <= end_dt
        else:
            return start_dt < dt < end_dt

    @staticmethod
    def add_days(value, days: int) -> datetime:
        dt = DateUtils.to_datetime(value)
        return dt + timedelta(days=days)

    @staticmethod
    def truncate_to_day(value) -> date:
        return DateUtils.to_datetime(value).date()

    @staticmethod
    def now() -> datetime:
        return datetime.now()

    @staticmethod
    def today() -> date:
        return date.today()
