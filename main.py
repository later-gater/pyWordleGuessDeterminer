from math import ceil
from master import master
from itertools import product


def makeAlphabet():
    return [[i, [], [], False] for i in "abcdefghijklmnopqrstuvwxyz"] 
    # every letter in the alphabet has 4 attributes:
        # 0: letter
        # 1: green locations, -empty array means no green, nums are location of yellow
        # 2: yellow locations, empty array means no yellow, nums are location of yellow
        # 3: grey, t/f

def getAlphaNum(letter): # turns letter into its corresponding location in alphab  et (into a number)
    try:
        return ord(letter.lower()) - 97
    except:
        print("probs not a letter, getAlphaNum error")


def getGuess(): # gets your guess
    while True:
        guess = input("What's your guess?\n")
        if guess in master:
            return guess
        else: print("word is not in list, try again")

def getFeedback(): # gets the feedback from the guess
    possibleInputs = ["0", "1", "2"]
    while True:
        youShallNotPass = False
        feedback = input("Type your word's colors as 0 (grey), 1 (yellow), and 2 (green). Should look like this: \"00201\"\n")
        for i in feedback:
            if i not in possibleInputs: #checks if all of the inputs are 0,1,2
                youShallNotPass = True
        # check if length
        if len(feedback) != 5:
            youShallNotPass = True
        if youShallNotPass == False:
            return feedback
        else: print("incorrect input")

def incorporateInfo(guess, feedback, alphabet): # uses the guess and feedback to alter alphabet (i.e. put info into alphabet)
    for i in range(len(guess)): # for every letter in the guess, check feedback to see which color the letter becomes
        if feedback[i] == "0":
            alphabet[getAlphaNum(guess[i])][3] = True
            # turn gray
        elif feedback[i] == '1':
            alphabet[getAlphaNum(guess[i])][2].append(i)
            #turn yellow
        elif feedback[i] == '2':
            alphabet[getAlphaNum(guess[i])][1].append(i)
            #turn green

def removeIncorrectGuesses(possible_guesses, alphabet, remove=True): # removes incorrect guesses from possible guesses using alphabet
    #Should I make this getIncorrectGuesses and then make a different func to removeWrongGuesses with WrongGuess as an input? 
    wrong_guesses = []
    for letter in alphabet:
        if len(letter[1]) > 0:
            for possible_word in possible_guesses:
                if possible_word not in wrong_guesses:
                    for green in letter[1]:
                        if letter[0] != possible_word[green]:
                            wrong_guesses.append(possible_word) # if word does not have letter in green, not valid guess
                    
                # eliminate the words in possible_guesses that don't have these letters in the right places
        if len(letter[2]) > 0:
            for possible_word in possible_guesses:
                if possible_word not in wrong_guesses:
                    for yellow in letter[2]:
                        if letter[0] == possible_word[yellow]: # if letter is in same place as yellow, not valid guess
                            wrong_guesses.append(possible_word)
                    if letter[0] not in possible_word: # if word is missing yellow letter, not valid guess
                        wrong_guesses.append(possible_word)
                # eliminate the words in possible_guesses that do have these letters in this place AND words that don't have this letter
        if letter[3] == True:
            for possible_word in possible_guesses:
                if letter[0] in possible_word:
                    if possible_word not in wrong_guesses:
                            wrong_guesses.append(possible_word) # if word has gray letter, not valid guess
    if remove:
        for i in wrong_guesses:
            if i in possible_guesses:
                possible_guesses.remove(i)
    else: 
        # print(len(wrong_guesses))
        return wrong_guesses
                        

    # print(possible_guesses)
    # print(len(possible_guesses))



perms = list(product([0, 1, 2], repeat=5))
perm_array = []

for i in range(len(perms)):
        perm_array.append("")
        for num in perms[i]:
            perm_array[i] = perm_array[i] + str(num)

perm_array.sort(reverse=True)
# gets all of the permutations that the word feedback could be

def getGuessLog(guess, guesses_possible):
    len_of_wrong_guesses = {} 
    for perm in perm_array:
        change_alpha = makeAlphabet() 
        incorporateInfo(guess, perm, change_alpha)
        # change the alphabet using incorporateInfo
        len_of_wrong_guesses[perm] = len(removeIncorrectGuesses(guesses_possible, change_alpha, False))
        # create a dict of all of the {permutation: how many incorrect guesses it eliminates}
      # honestly idk why i went with a dict it overcomplicates everything so much but it made it so easy to debug at the time and now i dont feel like changing it back
    return len_of_wrong_guesses

def sortGuessLog(guess_log):
    return {k : v for (k, v) in sorted(guess_log.items(), key=lambda x: x[1])}

def pruneGuessLog(guess_log, possible_guesses): # removes guesses that are not physically possible, definitely tons of bugs
    deleters = []
    for guess_num in range(len(guess_log)):
        if list(guess_log.values())[guess_num] >= len(possible_guesses):
            deleters.append(list(guess_log.keys())[guess_num])
    
    for i in deleters:
        del guess_log[i]
    
def getGuessLogStats(pruned_guess_log): # returns avg guesses removed, basically assign number to guess quality (bigger num better)
    return sum(pruned_guess_log.values()) / len(pruned_guess_log)
    # maybe i should give this a number that is not affected by the length of the pruned guess log



def compareAllWords(possible_guesses): 
    word_dict = {}
    print("Determining which word is best...")
    for word_num in range(len(possible_guesses)):
        guess_log = getGuessLog(possible_guesses[word_num], possible_guesses)
        pruneGuessLog(guess_log, possible_guesses)
        word_dict[possible_guesses[word_num]] = getGuessLogStats(guess_log)
        print(f"{possible_guesses[word_num]} has a score of {getGuessLogStats(guess_log)}")
        if word_num % ceil(len(possible_guesses)/10) == 0:
            print(f"{round(round(word_num/len(possible_guesses) * 100, -1))}% complete") # progress bar
    # print("100% complete") # only sometimes needs this, probably due to rounding error. idk
    return sortGuessLog(word_dict)




valid_guesses = master.copy()
invalid_guesses = []

letter_data = makeAlphabet()


while True:
    incorporateInfo(getGuess(), getFeedback(), letter_data)

    removeIncorrectGuesses(valid_guesses, letter_data)

    print(f"length of process is {len(valid_guesses)} words, estimated wait time is {ceil(len(valid_guesses)/5)} seconds")

    sorted_guesses = compareAllWords(valid_guesses) # much better would be to use master instead of valid_guesses but take wayyyy too long
  
    if len(sorted_guesses) > 1:
        print(f"""{list(sorted_guesses.keys())[-1]} is the best word with a score of {round(list(sorted_guesses.values())[-1], 2)}/{len(valid_guesses)} (AKA {round((list(sorted_guesses.values())[-1]/len(valid_guesses)*100))}/100), followed by {list(sorted_guesses.keys())[-2]} with a score of {round(list(sorted_guesses.values())[-2], 2)}/{len(valid_guesses)} (AKA {round((list(sorted_guesses.values())[-1]/len(valid_guesses)*100))}/100)""") # gives both best and second-best words the same score for some reason
    else: 
        print(f"The answer is {list(sorted_guesses.keys())[-1]}")
        break
