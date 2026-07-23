"""
--------------------
Section1 : IMPORTS
--------------------

    SM-MB-22July-2026 - Database configuration with SQLAlchemy engine.
    This file defines the database engine, session factory, and Base class.
    I am commenting each and every line for clarity and future reference

    FastAPI: Provides the web framework.
        FastAPI → creates the app.
        Depends → dependency injection (used for DB sessions).
        HTTPException → raises HTTP errors.
        status → constants for HTTP status codes.
    
    SQLAlchemy ORM: Session is the DB session class.
    Pydantic: 
        BaseModel → defines request/response schemas with validation.
        ConfigDict → v2 way to configure models.
        field_validator → v2 way to validate/transform fields.

    models: Your own file with SQLAlchemy ORM classes (User, BookItem, StateHistory, Order).
    database: Your own file with DB engine and session factory (engine, SessionLocal).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers import auth, inventory, order, admin

"""
--------------------
Section2 : DATABASE INITIALIZATION
--------------------

Background: SQLAlchemy inspects all models defined in models.Base and creates tables in the database if they don’t exist.
Calls: models.Base (your declarative base), engine (from database.py).        
"""
models.Base.metadata.create_all(bind=engine)

"""
--------------------
Section3 : FASTAPI APPLICATION
--------------------
Creates the FastAPI application object.
Background: This object registers routes (@app.get, @app.post) and runs the web server.
"""
app = FastAPI(title="MonkeyBarrow Inventory Management")

"""
--------------------
Section4 : CORS CONFIGURATION
--------------------
Enables Cross-Origin Resource Sharing so Flutter web/mobile can access the API.
Background: CORS headers allow requests from different origins (domains/ports).
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (in production, specify exact domains)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
app.include_router(order.router, prefix="/api/shopify", tags=["shopify"])

# Server startup
if __name__ == "__main__":
    import uvicorn
    # Listen on 0.0.0.0:8000 to accept requests from all network interfaces
    uvicorn.run(app, host="0.0.0.0", port=8009)
