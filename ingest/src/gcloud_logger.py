from google.cloud.logging.handlers import CloudLoggingHandler

import google.cloud.logging
import logging


def gcloud_logger(name):
    # Instantiate Google Cloud logger client
    gcloud_log_client = google.cloud.logging.Client()

    # Create custom handler
    handler = CloudLoggingHandler(gcloud_log_client)
    formatter = logging.Formatter(" %(levelname)s : %(message)s")
    handler.setFormatter(formatter)
    
    # Create logging handlers using standard library (by default will be sent to Logging)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger