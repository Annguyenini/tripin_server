def smart_cast(value):
    if isinstance(value,(int,float)):
        return value
    elif isinstance(value,str):
        if value.isdigit():
            return int(value)
        else:
            try:
                return float(value)
           
            except ValueError:
                pass
    return value