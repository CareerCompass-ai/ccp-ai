# logging_config.py
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Create a logger instance
logger = logging.getLogger(__name__)
