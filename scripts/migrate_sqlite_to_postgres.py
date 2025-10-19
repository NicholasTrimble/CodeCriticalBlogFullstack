import os
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.exc import SQLAlchemyError

# Local SQLite database
sqlite_uri = "sqlite:///app.db"
# Postgres from environment
postgres_uri = os.environ.get("DATABASE_URL")
if not postgres_uri:
    raise RuntimeError("Please set DATABASE_URL environment variable to your Postgres DB")

engine_sqlite = create_engine(sqlite_uri)
engine_pg = create_engine(postgres_uri)

# Create MetaData objects without bind
meta_sqlite = MetaData()
meta_sqlite.reflect(bind=engine_sqlite)

meta_pg = MetaData()
meta_pg.reflect(bind=engine_pg)

def copy_table(table_name):
    if table_name not in meta_sqlite.tables or table_name not in meta_pg.tables:
        print(f"Skipping {table_name}, table missing")
        return

    t_sql = Table(table_name, meta_sqlite, autoload_with=engine_sqlite)
    t_pg = Table(table_name, meta_pg, autoload_with=engine_pg)

    sel = select(t_sql)
    with engine_sqlite.connect() as src, engine_pg.connect() as dst:
        rows = src.execute(sel).mappings().all()
        print(f"Copying {len(rows)} rows from {table_name}")
        for row in rows:
            try:
                dst.execute(t_pg.insert().values(**row))
            except SQLAlchemyError as e:
                print("  skipping row:", e)
        dst.commit()
    print(f"Finished {table_name}")

if __name__ == "__main__":
    for t in ["post", "contact_message", "review"]:
        copy_table(t)
