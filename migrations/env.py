from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool,text
from alembic import context
import dotenv
import os
dotenv.load_dotenv()

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # build URL from env vars
        # Retrieve URL from environment or settings
    url = os.environ.get('DATABASE_URL') 
    print(url)
    
    if not url:
        raise ValueError('Database url is none')
    config.set_main_option("sqlalchemy.url", url)

    # use sqlalchemy engine like the original
    configuration = config.get_section(config.config_ini_section, {})
    configuration['sqlalchemy.url'] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS tripin_migrations"))
        connection.commit()
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema='tripin_migrations'
            
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()