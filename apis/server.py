from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes the ADK Runner when the app starts and shuts it down when the app stops."""
    global runner
    try:
        # Initialize the ADK runner with the root agent
        runner = Runner(agent=sage_flow)
        sage_logger.info("ADK Runner initialized with OpsSage Supervisor Agent.")
        yield
    except Exception as e:
        sage_logger.error(f"Failed to initialize ADK Runner: {e}")
        # Allow the application to start even if ADK initialization fails, but mark it
        raise e


app = FastAPI(
    title="OpsSage API",
    description="APIs for OpsSage System",
    version="1.0.0",  # TODO: Dynamic version
    lifespan=lifespan,
)
