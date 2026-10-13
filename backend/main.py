"""
    SM-MB-24July-2026 - instead one monolythic main file, we have created micro services and smaller programsDatabase configuration with SQLAlchemy engine.
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
""" 
--------------------
Section1 : IMPORTS
--------------------

"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
#from MonkeyBarrow.backend.routers import inventory
from routers import inventory
#from routers import gcsuploader
from routers import update_inventory_state
import models
from database import engine
from routers import auth, order, admin

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
app.mount("/static", StaticFiles(directory="D:/MonkeyBarrow/backend/static"), name="static")

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


# ✅ Root route for quick health check
@app.get("/")
def root():
    return {"message": "MonkeyBarrow API is running", "status": "ok"}

# ✅ Optional favicon route
#@app.get("/favicon.ico")
#def favicon():
#    return FileResponse("static/favicon.ico")

# Routers

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
app.include_router(update_inventory_state.router, prefix="/api/update_inventory_state", tags=["update_inventory_state"])                                                                            
app.include_router(order.router, prefix="/api/shopify", tags=["shopify"])
#app.include_router(gcsuploader.router, prefix="/api/gcsuploader", tags=["gcsuploader"])

# Server startup
if __name__ == "__main__":
    import uvicorn
    # Listen on 0.0.0.0:8000 to accept requests from all network interfaces
    uvicorn.run(app, host="0.0.0.0", port=8089)
#----------------------------------------------
# End of Program # SM: 28 July 2026
#----------------------------------------------   