with open('app/main.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'from app.api.v1.endpoints import auth, routes, schedules, seats, bookings, tickets',
    'from app.api.v1.endpoints import auth, routes, schedules, seats, bookings, tickets, tracking'
)

old_line = 'app.include_router(tickets.router,'
new_line = 'app.include_router(tracking.router,  prefix="/api/v1/tracking", tags=["Rastreo"])\n' + old_line
c = c.replace(old_line, new_line)

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('OK: main.py actualizado')