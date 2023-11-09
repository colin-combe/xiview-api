import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.api:app",
                host="0.0.0.0",
                port=6000,
                reload=True,
                log_level="info",  # Set the desired log level ("debug", "info", "warning", etc.)
                log_config="logging.ini"  # Specify the path to your logging configuration file
                )
