import os
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import create_engine
from alembic import context
from db.base import Base
from db.models import User, Order, Bid  # импортируем все модели

# Load .env
load_dotenv()
USER = os.getenv("DB_USER")
PASS = os.getenv("DB_PASS")
HOST = os.getenv("DB_HOST", "localhost")
PORT = os.getenv("DB_PORT", "3306")
NAME = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{USER}:{PASS}@{HOST}:{PORT}/{NAME}?charset=utf8mb4"

# Alembic config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=SQLALCHEMY_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(SQLALCHEMY_DATABASE_URL)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,       # важно для MySQL
            compare_type=True,          # проверка типов колонок
            compare_server_default=True # проверка дефолтных значений
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
