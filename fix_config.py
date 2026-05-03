with open("app/config.py", "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("@localhost:5432/boliviabus", "@localhost:5432/boliviabus_db")
with open("app/config.py", "w", encoding="utf-8") as f:
    f.write(c)

with open("alembic/env.py", "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("@localhost:5432/boliviabus", "@localhost:5432/boliviabus_db")
with open("alembic/env.py", "w", encoding="utf-8") as f:
    f.write(c)

print("config.py y alembic/env.py actualizados OK")