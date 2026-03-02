def validate_age_decorator(func):
    def wrapper(age):
        if age < 0 or age > 120:
            raise ValueError("Invalid age")
        return func(age)
    return wrapper

@validate_age_decorator
def set_user_age(age,name):
    print(f"name set to {name}")
    print(f"Age set to {age}")
    
set_user_age(1111,'an')