import os
from sqlalchemy import create_engine, text

url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/db_pramuka_jabar')
print('URL', url)
engine = create_engine(url, connect_args={'connect_timeout': 5})
try:
    with engine.connect() as conn:
        result = conn.execute(text('select 1'))
        print(result.scalar())
        print('connected')
except Exception as e:
    print('ERROR', type(e).__name__, e)
