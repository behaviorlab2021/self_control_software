import datetime
def datetime_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Type {obj.__class__.__name__} not serializable")
