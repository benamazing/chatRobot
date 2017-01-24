import logging
import logging.config

logging.config.fileConfig("../logger.conf")

cron_logger = logging.getLogger("cron")
app_logger = logging.getLogger("app")