from src.other.controller import Controller
import src.other.logging_config as log


if __name__ == "__main__":
    log.apply()
    c = Controller()
    c.run()
