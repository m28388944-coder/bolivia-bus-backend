from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import logging

from app.routers.deps import get_current_user
from app.models import User
from app.models.user import RolUsuario
from app.database import get_db

router = APIRouter(prefix="/dev", tags=["developer"])
logger = logging.getLogger(__name__)

FORBIDDEN = [
    "DROP DATABASE", "DROP SCHEMA", "TRUNCATE",
    "PG_TERMINATE_BACKEND", "PG_RELOAD_CONF",
    "COPY TO", "COPY FROM"
]

def require_developer(current_user: User = Depends(get_current_user)):
    if current_user.rol != RolUsuario.developer:
        raise HTTPException(status_code=403, detail="Acceso solo para desarrolladores")
    return current_user

class SQLRequest(BaseModel):
    query: str
    limit: int = 100

@router.post("/sql")
def execute_sql(
    req: SQLRequest,
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    query = req.query.strip()
    if not query:
        raise HTTPException(400, "Query vacia")

    upper = query.upper()
    for kw in FORBIDDEN:
        if kw in upper:
            raise HTTPException(403, f"Operacion no permitida: {kw}")

    query = query.rstrip(";").strip()
    upper = query.upper()
    if upper.startswith("SELECT") and "LIMIT" not in upper:
        query = f"{query} LIMIT {req.limit}"

    start = time.time()
    try:
        result = db.execute(text(query))
        elapsed = round((time.time() - start) * 1000, 2)

        if result.returns_rows:
            columns = list(result.keys())
            rows = [[str(v) if v is not None else None for v in row] for row in result.fetchall()]
            row_count = len(rows)
        else:
            columns = ["affected_rows"]
            rows = [[str(result.rowcount)]]
            row_count = result.rowcount
            db.commit()

        logger.info(f"DEV SQL | {dev.email} | {query[:80]}")
        return {
            "columns": columns,
            "rows": rows,
            "row_count": row_count,
            "execution_time_ms": elapsed,
            "query_type": upper.split()[0]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(400, str(e))

@router.get("/sql/tables")
def get_tables(
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    result = db.execute(text("""
        SELECT relname as tablename, n_live_tup::integer as row_count
        FROM pg_stat_user_tables
        ORDER BY relname
    """))
    return [{"name": r[0], "rows": r[1]} for r in result.fetchall()]

@router.get("/sql/schema/{table}")
def get_schema(
    table: str,
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    result = db.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = :table
        ORDER BY ordinal_position
    """), {"table": table})
    return [{"column": r[0], "type": r[1], "nullable": r[2]} for r in result.fetchall()]

@router.get("/sql/debug")
def debug_tables(
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    import traceback
    try:
        result = db.execute(text("""
            SELECT tablename, n_live_tup::integer as row_count
            FROM pg_stat_user_tables
            ORDER BY tablename
        """))
        return [{"name": r[0], "rows": r[1]} for r in result.fetchall()]
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}


