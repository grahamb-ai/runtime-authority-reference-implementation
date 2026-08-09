## @file config.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Application configuration, loaded from environment variables with local defaults.
#


import os

from dotenv import load_dotenv

# Populate os.environ from a local .env file if one exists. Real environment
# variables (e.g. those injected in production) take precedence over .env.
load_dotenv()

# SQLAlchemy/SQLModel connection string. The default targets a local Postgres;
# production overrides it via the DATABASE_URL environment variable.
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/authority_poc",
)

# Free-form environment label ("development", "production", ...).
ENV: str = os.getenv("ENV", "development")

# Convenience flag derived from ENV. Drives SQL echo logging (see database.py).
DEBUG: bool = ENV == "development"
