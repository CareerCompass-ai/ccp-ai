"""
This module contains the main entry point for starting the server.
"""

import uvicorn

import constant.config as cfg
from pkg.logging import logger

if __name__ == "__main__":
    logger.info("-------------------------------Starting server-------------------------------")
    try:
        logger.info("""
                      _oo0oo_
                     o8888888o
                     88" . "88
                     (| -_- |)
                     0\  =  /0
                   ___/`---'\___
                 .' \\|     |// '.
                / \\|||  :  |||// \\
               / _||||| -:- |||||- \\
              |   | \\\  -  /// |   |
              | \_|  ''\---/''  |_/ |
              \  .-\__  '-'  ___/-. /
            ___'. .'  /--.--\  `. .'___
         ."" '<  `.___\_<|>_/___.' >' "".
        | | :  `- \`.;`\ _ /`;.`/ - ` : | |
        \  \ `_.   \_ __\ /__ _/   .-` /  /
    =====`-.____`.___ \_____/___.-`___.-'=====
                      `=---='

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
       Phật phù hộ, app chạy đừng lỗi nha app ơi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
""")

        uvicorn.run("app.server:app", host="0.0.0.0", port=int(cfg.HTTP_PORT), reload=False)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        raise  # Re-raise the KeyboardInterrupt to exit cleanly
    except ValueError as ve:
        logger.error("Server encountered a ValueError: %s", ve)
    except Exception as e:
        logger.exception("Server encountered an unexpected error: %s", e)
        raise  # Re-raise the exception for further handling or debugging
    finally:
        logger.info("-------------------------------Server stopped-------------------------------")
