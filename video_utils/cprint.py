from colorama import Fore, Style, init

def cprint(colour, message):
    colours = {
            "green": Fore.GREEN,
            "blue": Fore.BLUE,
            "red": Fore.RED,
            "yellow": Fore.YELLOW
            }
    print(colours[colour] + str(message) + Style.RESET_ALL)
