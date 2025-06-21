class bcolors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    INVERT = '\033[7m'
    HIDDEN = '\033[8m'

class ColorDisplay(bcolors):
    # https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797

    def print(self, message, *colors, end="\n"):
        """
        Affiche le message avec les combinaisons de couleurs données

        Parameters
        ----------
        message:str
            Texte à afficher
        colors:str
            Soit le nom d'un attribut de bcolors soit un caractère directement
        end:str
            à afficher à la fin du message, par défaut \n
        """
        
        print(f'{"".join([getattr(bcolors, color) if hasattr(bcolors, color) else color for color in colors])}{message}{bcolors.RESET}', end=end)

    def error(self, message):
        self.print("ERREUR", self.RED, self.UNDERLINE, self.BOLD, end=f"{self.YELLOW} > {self.RESET}")
        self.print(message, self.RED, self.ITALIC)

a = ColorDisplay()
a.error("Message d'erreur")