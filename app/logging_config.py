import logging
from pathlib import Path


def configure_logging(app):
    """
    Konfigurasi logger utama aplikasi CIMS.
    """

    logger = logging.getLogger(app.config["APP_NAME"])

    log_level = getattr(
        logging,
        app.config["LOG_LEVEL"].upper(),
        logging.INFO,
    )

    logger.setLevel(log_level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    # ==========================
    # Console Handler
    # ==========================

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # ==========================
    # File Handler
    # ==========================

    log_folder = Path(app.config["LOG_FOLDER"])
    log_folder.mkdir(exist_ok=True)

    log_file = log_folder / "cims.log"

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8",
    )

    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_logger(name=None):
    """
    Mengambil logger aplikasi CIMS.

    Contoh:
        logger = get_logger(__name__)
    """

    app_logger = logging.getLogger("CIMS")

    if name:
        return app_logger.getChild(name)

    return app_logger