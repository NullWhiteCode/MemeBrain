"""Read and update MemeBrain's local configuration."""

import json
from pathlib import Path

from model_selection import current_caption_model, update_caption_model


CONFIG_FILE = Path("config.json")


def load_config():
    """Return the complete configuration dictionary.

    Returns an empty dictionary when no configuration file exists.
    """
    if not CONFIG_FILE.exists():
        return {}

    json_data = CONFIG_FILE.read_text(encoding="utf-8")
    return json.loads(json_data)


def save_config(config):
    """Write the complete configuration dictionary to disk."""
    json_data = json.dumps(config, indent=2)
    CONFIG_FILE.write_text(json_data, encoding="utf-8")


def save_library_path(folder_path):
    """Store the selected library path in the configuration file."""
    config = load_config()
    config["library_path"] = str(folder_path)
    save_config(config)


def load_library_path():
    """Return the saved library path, or None if none is configured."""
    return load_config().get("library_path")


def save_current_folder(folder_path):
    """Store the folder currently being viewed relative to the library."""
    config = load_config()
    config["current_folder"] = str(folder_path)
    save_config(config)


def load_current_folder():
    """Return the saved current folder, or None if none is configured."""
    return load_config().get("current_folder")


def load_caption_model():
    """Read the saved preference from config.json."""
    config_caption = load_config().get("caption_model")
    
    if config_caption:
        update_caption_model(config_caption)

    
def save_caption_model():
    """Write the current selection to config.json."""
    config = load_config()
    model = current_caption_model()
    
    if model:
        config["caption_model"] = str(model)
        save_config(config)
        
        
def clear_saved_caption_model():
    """Clears the saved caption model from config.json."""
    config = load_config()
    config["caption_model"] = ""
    save_config(config)
    
    

    