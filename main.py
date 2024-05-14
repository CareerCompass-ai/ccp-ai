import uvicorn
from app.server import app
import constant.config as cfg

import logging
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

if __name__ == "__main__":
    logging.info("-------------------------------Starting server-------------------------------")
    try:
        uvicorn.run("app.server:app", host="0.0.0.0", port=int(cfg.HTTP_PORT), reload=True)
    except KeyboardInterrupt:
        logging.info("Server interrupted by user")
    except Exception as e:
        logging.error(f"Server encountered an unexpected error: {e}")
    finally:
        logging.info("-------------------------------Server stopped-------------------------------")
