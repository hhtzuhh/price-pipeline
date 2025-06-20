from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.prices import router as prices_router
from app.api.poll import router as poll_router
from app.api.ma import router as ma_router
from dotenv import load_dotenv

# Import your scheduler instance.
# Ensure that `scheduler.start()` and `scheduler.shutdown()`
# are NOT called directly in app/core/scheduler.py at the module level.
from app.core.scheduler import scheduler

# This loads variables from .env into os.environ.
# Keep this here, as it's correctly placed for application startup.
load_dotenv()

# Define your lifespan context manager.
# This function will be called by FastAPI during its startup and shutdown phases.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Events ---
    print("FastAPI application startup initiated.")

    # Initialize and start APScheduler here.
    # This ensures the event loop is running before scheduler.start() is called.
    print("Starting APScheduler...")
    scheduler.start()

    # You might also put database connection setup here if needed, e.g.:
    # await database.connect() # Assuming you have a database connection pool

    yield  # This yields control to the FastAPI application, allowing it to handle requests.

    # --- Shutdown Events ---
    print("FastAPI application shutdown initiated.")

    # Shut down APScheduler gracefully when the application stops.
    print("Shutting down APScheduler...")
    scheduler.shutdown()

    # You might also close database connections here if needed, e.g.:
    # await database.disconnect() # Assuming you have a database connection pool

# Initialize your FastAPI app with the defined lifespan context.
app = FastAPI(title="Market-Data Service (Y-Finance only v0)", lifespan=lifespan)

# Include your API routers.
app.include_router(prices_router)
app.include_router(poll_router)
app.include_router(ma_router)

# Basic health check endpoint.
# You can extend this to check database connection, Kafka connectivity, etc.
@app.get("/health")
def health():
    # You might want to check the scheduler's status here too, e.g., scheduler.running
    return {"status": "ok", "scheduler_running": scheduler.running}

