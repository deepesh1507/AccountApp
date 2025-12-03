from pathlib import Path
import sys

APP_CONFIG = {
    "APP_NAME": "Professional Accounting Software",
    "VERSION": "1.0.0",
    "DATA_DIR": Path(__file__).resolve().parent.parent / "data",
    "RESOURCES_DIR": Path(__file__).resolve().parent.parent / "resources",
    "DEFAULT_WINDOW_SIZE": (1200, 700),
    "MIN_WINDOW_SIZE": (800, 600),
    "THEME": "light",
}

# Database configuration
DB_CONFIG = {
    "BACKUP_DIR": APP_CONFIG["DATA_DIR"] / "backups",
    "COMPANIES_FILE": APP_CONFIG["DATA_DIR"] / "companies.json",
    "COMPANIES_DIR": APP_CONFIG["DATA_DIR"] / "companies",
}

# Add these configurations
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "standard"
        },
    },
    "loggers": {
        "": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True
        }
    }
}

# UI Configuration
UI_CONFIG = {
    "PADDING": 10,
    "ENTRY_WIDTH": 300,
    "BUTTON_WIDTH": 120,
    "LABEL_WIDTH": 180
}

def load_config(config_path: str = "config.json") -> dict:
    """Load configuration from a JSON file.
    Returns defaults if file missing or malformed.
    """
    from pathlib import Path
    import json
    default = {
        "data_dir": "data",
        "use_sqlite": False,
        "sqlite_path": "data/accountapp.db",
    }
    cfg_path = Path(config_path)
    if not cfg_path.is_file():
        return default
    try:
        with cfg_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        cfg = default.copy()
        cfg.update(data)
        return cfg
    except Exception:
        return default
}
