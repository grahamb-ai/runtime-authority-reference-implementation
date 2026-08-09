## @file main.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Authority System FastAPI application entry point: builds and wires up the app.
#

"""Authority System — FastAPI application entry point.

Builds the app object, registers the routers, creates database tables on
startup, enables CORS for the local demo UI, and exposes a liveness
'/health' endpoint. Run in development with:

    fastapi dev main.py     # Swagger UI at http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_tables
from app.routers import orders, specs


@asynccontextmanager
## @fn lifespan(app)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Application lifespan hook, run once on startup before serving requests.
#  @param app The FastAPI application instance.
#  @return None. This is an async context manager generator used by FastAPI's startup/shutdown hooks.
async def lifespan(app: FastAPI):
    """Application lifespan: run once on startup, before serving requests.

    Here we ensure the schema exists. In production this responsibility moves to
    Alembic migrations, but auto-creation keeps the POC one command to run.
    """
    create_tables()
    yield
    # Nothing to tear down on shutdown for the POC


app = FastAPI(
    title="Authority System",
    description=(
        "Evaluates orders against authority and admissibility rules "
        "extracted from company policy documents. Returns ALLOW / ESCALATE / REFUSE"
        "with a finalised decision record."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# CORS -> permissive for the POC so the local demo UI (opened as a file:// page
# or served from another port can call the API from the browser. Tighten
# allow_origins to specific origins before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wire up the two feature routers
app.include_router(specs.router)
app.include_router(orders.router)


@app.get("/health", tags=["health"])
## @fn health()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Simple liveness probe endpoint.
#  @return A small status dictionary confirming the service is running
#
def health() -> dict[str, str]:
    """Simple liveness probe."""
    return {"status": "ok", "version": "0.1.0"}
