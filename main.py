import uvicorn

from app.api import app

if __name__ == "__main__":
    uvicorn.run(app,
                host="0.0.0.0",
                port=3000,
                log_level="info",  # Set the desired log level ("debug", "info", "warning", etc.)
                log_config="logging.ini",  # Specify the path to your logging configuration file
                timeout_keep_alive=300,  # Keep-alive timeout in seconds
                )
