from fileinput import filename
import os
import logging


def is_config_folder(path):
    """
    Checks a path contains
    """
    boons = False
    config = False
    for _, _, files in os.walk(path):
        logging.debug(f"files: {files}")
        for file in files:
            if file.lower() == "boons.json":
                boons = True
            elif file.lower() == "config.json":
                config = True
            logging.debug(f"{file}: boons: {boons}, config: {config}")

    return boons and config


def get_configs(path):
    """
    Takes a path and gets valid config folders
    """
    config_dirs = []
    dirs = next(os.walk(path))[1]
    for dir in dirs:
        logging.debug(f"dir: {os.path.join(path,dir)}")
        if is_config_folder(os.path.join(path, dir)):
            config_dirs.append(os.path.join(path, dir))
    logging.debug(config_dirs)
    return config_dirs
