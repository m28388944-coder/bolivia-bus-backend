from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import dev, dev_sql, auth, users, schedules, bookings, terminals, companies, tracking, notifications

app = FastAPI(title="Bolivia Bus API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix="/auth",      tags=["auth"])
app.include_router(users.router,     prefix="/users",     tags=["users"])
app.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
app.include_router(bookings.router,  prefix="/bookings",  tags=["bookings"])
app.include_router(terminals.router, prefix="/terminals", tags=["terminals"])
app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(tracking.router,  prefix="/tracking",  tags=["tracking"])
app.include_router(dev.router,       tags=["developer"])
app.include_router(dev_sql.router,   tags=["developer"])
app.include_router(notifications.router, tags=["notifications"])

@app.get("/")
def root():
    return {"status": "ok", "sistema": "Bolivia Bus API v1.0"}




