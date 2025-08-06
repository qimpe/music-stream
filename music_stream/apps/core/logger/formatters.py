import logging

from colorama import Fore, Style


class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record) -> str:
        if record.levelno in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelno]}{record.levelname}{Style.RESET_ALL}"
            record.msg = f"{self.COLORS[record.levelno]}{record.msg}{Style.RESET_ALL}"
        return super().format(record)
