import src.common.logging_config as log
from src.helpers.controller import Controller

if __name__ == "__main__":
    log.apply()
    c = Controller()
    c.run()
