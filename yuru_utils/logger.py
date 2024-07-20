from logging import getLogger, handlers, StreamHandler, Formatter, INFO

def setup_logger(name: str, log_file: str):
    logger = getLogger(name)
    logger.setLevel(INFO)
    
    rot_file_handler = handlers.RotatingFileHandler(
        filename=log_file,
        encoding="utf-8",
        maxBytes=32*1024*1024,
        backupCount=5,
    )
    
    date_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", date_fmt, style='{')
    rot_file_handler.setFormatter(formatter)
    logger.addHandler(rot_file_handler)

    stream_handler = StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    logger.info("Successfully configured the logger.")
    return logger

def get_logger(name: str):
    return getLogger(name)