import os

# generate path from bibtex code:
def generatePublPath(pathToMemex, bibTexCode):
    temp = bibTexCode.lower()
    directory = os.path.join(pathToMemex, temp[0], temp[:2], bibTexCode)
    return(directory)