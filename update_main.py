with open("app/main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "from app.routers import auth, users, schedules, bookings, terminals",
    "from app.routers import auth, users, schedules, bookings, terminals, companies"
)
content = content.replace(
    'app.include_router(terminals.router, prefix="/terminals", tags=["terminals"])',
    'app.include_router(terminals.router, prefix="/terminals", tags=["terminals"])\napp.include_router(companies.router, prefix="/companies", tags=["companies"])'
)
with open("app/main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("OK: main.py actualizado")