from src.helpers.controller import Controller
import src.common.logging_config as log


if __name__ == "__main__":
    log.apply()
    c = Controller()
    c.run()
