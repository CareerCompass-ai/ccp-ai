import uvicorn

import constant.config as cfg
from pkg.logging import logger

if __name__ == "__main__":
    logger.info("-------------------------------Starting server-------------------------------")
    try:
        uvicorn.run("app.server:app", host="0.0.0.0", port=int(cfg.HTTP_PORT), reload=False)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server encountered an unexpected error: {e}")
    finally:
        logger.info("-------------------------------Server stopped-------------------------------")
