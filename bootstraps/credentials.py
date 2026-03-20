import os 
import dotenv
import signal
dotenv.load_dotenv()

def bootstrapping_credentials():
    MISSING =[]
    OPTIONS=[]
    DB_HOST= os.getenv('DB_HOST') or MISSING.append('DB_HOST')
    DB_PORT= os.getenv('DB_PORT') or MISSING.append('DB_PORT')
    DB_USER= os.getenv('DB_USER') or MISSING.append('DB_USER')
    DB_PASS= os.getenv('DB_PASS') or MISSING.append('DB_PASS')
    DB_NAME= os.getenv('DB_NAME') or MISSING.append('DB_NAME')
    
    AWS_ACCESS_KEY_ID= os.getenv('AWS_ACCESS_KEY_ID') or MISSING.append('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY= os.getenv('AWS_SECRET_ACCESS_KEY') or MISSING.append('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION= os.getenv('AWS_DEFAULT_REGION') or MISSING.append('AWS_DEFAULT_REGION')

    EMAIL_USERNAME= os.getenv('EMAIL_USERNAME') or MISSING.append('EMAIL_USERNAME')
    EMAIL_PASSWORD= os.getenv('EMAIL_PASSWORD') or MISSING.append('EMAIL_PASSWORD')
    MAIL_DEFAULT_SENDER= os.getenv('MAIL_DEFAULT_SENDER') or MISSING.append('MAIL_DEFAULT_SENDER')

    REDIS_PORT= os.getenv('REDIS_PORT') or MISSING.append('DB_NAREDIS_PORTME')
    REDIS_HOST= os.getenv('REDIS_HOST') or MISSING.append('REDIS_HOST')

    MAPBOX_PUBLIC_KEY= os.getenv('MAPBOX_PUBLIC_KEY') or OPTIONS.append('MAPBOX_PUBLIC_KEY')

    DATABASE_URL= os.getenv('DATABASE_URL') or MISSING.append('DATABASE_URL')

    BASE_URL= os.getenv('BASE_URL') or MISSING.append('BASE_URL')
    
    DISCORD_ERROR_WEBHOOK= os.getenv('DISCORD_ERROR_WEBHOOK') or OPTIONS.append('DISCORD_ERROR_WEBHOOK')
    DISCORD_REQUEST_WEBHOOK= os.getenv('DISCORD_REQUEST_WEBHOOK') or OPTIONS.append('DISCORD_REQUEST_WEBHOOK')
    DISCORD_STATUS_WEBHOOK= os.getenv('DISCORD_STATUS_WEBHOOK') or OPTIONS.append('DISCORD_STATUS_WEBHOOK')
    if OPTIONS:
        print('Missing option credential, these will not effect the running: \n')
        for miss in OPTIONS:
            print(miss + '\n')
    if MISSING:
        print('Missing critical credentials NEED to add to env: \n')
        for miss in MISSING:
            print(miss + '\n')
        os.kill(os.getppid(), signal.SIGTERM)  # kill the gunicorn master
        os._exit(1)
    

