import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, inspect as sa_inspect
from app.database import engine, Base
from app.routes import auth, locations, categories, dishes, banners, staff, orders, footer, upload

# Create new tables (won't alter existing ones)
Base.metadata.create_all(bind=engine)

# Manual migrations for added columns on existing tables
with engine.connect() as conn:
    cols = [c["name"] for c in sa_inspect(engine).get_columns("dishes")]
    if "active" not in cols:
        conn.execute(text("ALTER TABLE dishes ADD COLUMN active BOOLEAN NOT NULL DEFAULT TRUE"))
        conn.commit()

app = FastAPI(title="Mamyr Cafe API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routes under /api
app.include_router(auth.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(dishes.router, prefix="/api")
app.include_router(banners.router, prefix="/api")
app.include_router(staff.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(footer.router, prefix="/api")
app.include_router(upload.router, prefix="/api")


@app.get("/")
def root():
    return {"status": "ok", "app": "Mamyr Cafe API"}
