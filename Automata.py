#every state is an object that has a name and a list of possible transitions and if it can be repeated

from Tokens import IF, ID, ELSE, SKIP
from Tokens import letters, numbers, epsilon, space


class State:

    def __init__(self, name, transitions, is_repeated = False, is_final = False, is_start = False):

        self.name = name
        self.is_repeated = is_repeated
        self.transitions = transitions
        self.is_final = is_final
        self.is_start = is_start

    def add_transition(self, char, next_state):

        self.transitions.append((char, next_state))

    def __repr__(self):

        return self.name

def state_maker(token):


#function that takes a token and builds states from it

        start = State("q0", [], is_start = True)
        currentState = start
        stateIndex = 1

        for chars, repeats in token.string: 

            if repeats:

                currentState.add_transition(chars, currentState)
                currentState.is_repeated = True

            else:

                nextState = State(f"q{stateIndex}", [])
                currentState.add_transition(chars, nextState)
                currentState = nextState
                stateIndex += 1

        currentState.is_final = True
        currentState.tokenName = token.name

        return start

def number_states(start):

#gives every state a unique name

    visitedState = []
    toVisit = [start]

    while toVisit:

        currentState = toVisit.pop(0)

        if currentState in visitedState:
            continue
        visitedState.append(currentState)

        for chars, nextState in currentState.transitions:

            toVisit.append(nextState)

    for i, state in enumerate(visitedState):

        state.name = f"q{i}"

def union(tokens):

#merges all automatons into one using epsilon transitions from q0

    start = State("S", [], is_start = True)

    for token in tokens:

        tokenStart = state_maker(token)
        tokenStart.is_start = False
        start.add_transition(epsilon, tokenStart)

    number_states(start)

    return start

def all_states(start):

#returns every state reachable from start

    seen = []
    toVisit = [start]

    while toVisit:

        currentState = toVisit.pop(0)

        if currentState in seen:
            continue
        seen.append(currentState)

        for chars, nextState in currentState.transitions:
            toVisit.append(nextState)

    return seen


def epsilon_closure(state):

#every state reachable from this one using only epsilon arrows (including itself)

    closure = [state]
    toVisit = [state]

    while toVisit:

        currentState = toVisit.pop(0)

        for chars, nextState in currentState.transitions:

            if chars == epsilon and nextState not in closure:
                closure.append(nextState)
                toVisit.append(nextState)

    return closure


def remove_epsilon(start):

    states = all_states(start)
    new_data = {}

    # step 1: work out the new arrows for every state, without changing anything yet
    for state in states:

        new_transitions = []
        final = False
        token_name = None

        for s in epsilon_closure(state):

            if s.is_final and not final:        # the first final state found wins (token priority)
                final = True
                token_name = s.tokenName

            for chars, nextState in s.transitions:

                if chars != epsilon and (chars, nextState) not in new_transitions:
                    new_transitions.append((chars, nextState))

        new_data[state] = (new_transitions, final, token_name)

    # step 2: apply them
    for state in states:
        state.transitions, state.is_final, state.token_name = new_data[state]

    number_states(start)        # states that are no longer reachable disappear here
    return start

def printAutomata(start):

#function for taking the start of the automata and traverses with each iteration printing the transitions of the next state

    visitedState = []
    toVisit = [start]

    while toVisit:

        currentState = toVisit.pop(0)

        if currentState in visitedState:
            continue
        visitedState.append(currentState)

        for chars, nextState in currentState.transitions:

            if chars == letters :

                print (f"{currentState.name} --Letters--> {nextState.name}") #only for simplyfying letters instead of mashup of letters

            elif chars == letters + numbers:

                print (f"{currentState.name} --Letters + Numbers--> {nextState.name}") #only for simplyfying letters instead of mashup of letters and numbers

            else:

              print(f"{currentState.name} --{chars}--> {nextState.name}") #only for simplyfying letters instead of mashup of letters and numbers

            toVisit.append(nextState)

        if currentState.is_final == True:
                
                print (f"{currentState.name} Is Final! --> {currentState.tokenName}")




if __name__ == "__main__":
  
        printAutomata(remove_epsilon(union([IF, ID, SKIP, ELSE, ID])))