from datetime import datetime
from typing import Union

def date_comparator(date1 : Union[datetime, str], date2 : Union[datetime, str], FORMAT : str = '%Y-%m-%d %H:%M:%S%z') -> int:
    date1, date2 = [datetime.strptime(date, FORMAT) if type(date) == str else date for date in (date1, date2)]
    return (date1 > date2) - (date1 < date2)