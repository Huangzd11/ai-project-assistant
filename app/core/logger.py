import logging


def setup_logger(name: str = "ai-project-assistant") -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    return logging.getLogger(name)


logger = setup_logger()
