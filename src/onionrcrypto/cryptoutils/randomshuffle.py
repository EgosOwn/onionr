from random import SystemRandom

def random_shuffle(theList):
    myList = list(theList)
    SystemRandom().shuffle(myList)
    return myList