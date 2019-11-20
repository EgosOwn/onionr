import secrets
def random_shuffle(theList):
    myList = list(theList)
    shuffledList = []
    myListLength = len(myList) + 1
    while myListLength > 0:
        removed = secrets.randbelow(myListLength)
        try:
            shuffledList.append(myList.pop(removed))
        except IndexError:
            pass
        myListLength = len(myList)
    return shuffledList