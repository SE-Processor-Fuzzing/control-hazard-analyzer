from src.controller import Controller
import src.logging_config as log


if __name__ == "__main__":
    log.apply()
    c = Controller()
    c.run()
