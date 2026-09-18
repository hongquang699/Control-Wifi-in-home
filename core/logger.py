"""
Hệ thống ghi log tập trung cho Network Manager.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name="network_manager", log_file="data/logs/network_manager.log", level="INFO"):
    logger = logging.getLogger(name)
    
    # Nếu logger đã được cấu hình handlers thì không thêm lại
    if logger.handlers:
        return logger
        
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler có rotation
    try:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Không thể tạo file log tại {log_file}: {e}")
        
    return logger

logger = setup_logger()
