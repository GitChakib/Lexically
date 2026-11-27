

#NEEDED FOR MATCHING (instead of writing "L/N" just write letters + (same as or) numbers)
letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
numbers = "0123456789"
space = " \t\n\r"
epsilon = None       #ε transitions are counted as None since the character ε adds a character when epsilon in reality is empty



class Token:

    def __init__(self, name, string, skip = False):
        self.name = name
        self.string = string
        self.skip = skip


#defining our tokens

#every token is a tuple of a name and a list of characters and whether they can be repeated

space = " \t" 

IF = Token("IF", [("i", False), ("f", False)]) 
ID = Token("ID", [(letters, False), (letters + numbers, True)])
ELSE = Token("ELSE", [("e", False), ("l", False), ("s", False), ("e", False)])
SKIP = Token("WS", [(space, False), (space, True)], skip=True)
