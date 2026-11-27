#every state is an object that has a name and a list of possible transitions and if it can be repeated

from Tokens import IF, ID, ELSE, SKIP
from Tokens import letters, numbers, epsilon, space
with open("code.txt", "r", encoding="utf-8") as file:
    code = file.read()


class State:

    def __init__(self, name, transitions, is_repeated = False, is_final = False, is_start = False):

        self.name = name
        self.is_repeated = is_repeated
        self.transitions = transitions
        self.is_final = is_final
        self.is_start = is_start
        self.token_name = None

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
        currentState.token_name = token.name

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

def split_groups(labels):


    groups = {}       

    for label in labels:

        for char in label:

            signature = tuple(i for i, other in enumerate(labels) if char in other)

            if signature not in groups:
                groups[signature] = ""

            if char not in groups[signature]:
                groups[signature] += char

    return list(groups.values())


def remove_epsilon(start):

    states = all_states(start)
    new_data = {}

    
    for state in states:

        new_transitions = []
        final = False
        token_name = None

        for s in epsilon_closure(state):

            if s.is_final and not final:      
                final = True
                token_name = s.token_name

            for chars, nextState in s.transitions:

                if chars != epsilon and (chars, nextState) not in new_transitions:
                    new_transitions.append((chars, nextState))

        new_data[state] = (new_transitions, final, token_name)

    for state in states:
        state.transitions, state.is_final, state.token_name = new_data[state]

    number_states(start)        # states that are no longer reachable disappear here
    return start



def subset_diviser(start, tokens):

#turns the automaton (no epsilon arrows) into a deterministic one.
#every new state stands for a SET of old states.
#returns the new start state and a table (list of rows) describing every new state

    priority = {token.name: i for i, token in enumerate(tokens)} 

    def order(states):                                            
        return sorted(states, key = lambda s: int(s.name[1:]))

    def new_state(old_set):                                         

        state = State(f"D{len(dfa_states)}", [])
        finals = [s for s in old_set if s.is_final]

        if finals:

            winner = min(finals, key = lambda s: priority[s.token_name]) 

            state.is_final = True

            state.token_name = winner.token_name

        dfa_states[old_set] = state
        toVisit.append(old_set)
        return state

    dfa_states = {}             
    toVisit = []
    table = []

    dfa_start = new_state(frozenset([start]))
    dfa_start.is_start = True

    while toVisit:

        old_set = toVisit.pop(0)
        current = dfa_states[old_set]

        labels = []
        for s in order(old_set):
            for chars, nextState in s.transitions:
                labels.append(chars)

        row = {"state": current.name,
               "old states": "{" + ", ".join(s.name for s in order(old_set)) + "}",
               "arrows": [],
               "final": current.token_name}

        for group in split_groups(labels):

            targets = set()
            for s in old_set:
                for chars, nextState in s.transitions:
                    if group[0] in chars:                 
                        targets.add(nextState)

            target_set = frozenset(targets)

            if target_set not in dfa_states:
                new_state(target_set)

            current.add_transition(group, dfa_states[target_set])
            row["arrows"].append((group, dfa_states[target_set].name))

        table.append(row)

    return dfa_start, table


def tokenize(start, text, tokens):

#runs a block of text through the deterministic automaton and returns the list of tokens found.
#at each position it keeps reading as long as an arrow exists, remembers the LAST final state it
#passed (the longest match), then cuts the token there and starts again right after it

    skip_names = {token.name for token in tokens if token.skip}
    result = []
    pos = 0

    while pos < len(text):

        state = start
        i = pos
        last_final = None                           # (token name, end position)

        while i < len(text):

            nextState = None
            for chars, target in state.transitions:
                if text[i] in chars:
                    nextState = target
                    break

            if nextState is None:                   # no arrow for this character: stop
                break

            state = nextState
            i += 1

            if state.is_final:
                last_final = (state.token_name, i)

        line = text.count("\n", 0, pos) + 1
        column = pos - (text.rfind("\n", 0, pos) + 1) + 1

        if last_final is None:                      # nothing matched here: report the character, move on
            result.append({"token": "ERROR", "lexeme": text[pos], "line": line, "column": column})
            pos += 1
            continue

        name, end = last_final

        if name not in skip_names:
            result.append({"token": name, "lexeme": text[pos:end], "line": line, "column": column})

        pos = end

    return result




def minimize(start):

#merges states that behave identically.
#returns the new start state and a table (list of rows) describing every new state

    states = all_states(start)

    # the characters, split into groups that behave the same everywhere in the machine
    labels = []
    for s in states:
        for chars, nextState in s.transitions:
            if chars not in labels:
                labels.append(chars)
    alphabet = split_groups(labels)

    def move(state, group):                     # where does this group of characters lead? (None = nowhere)
        for chars, nextState in state.transitions:
            if group[0] in chars:
                return nextState
        return None

    # first partition: split by "is it final, and for which token"
    block = {}
    kinds = {}
    for s in states:
        kind = (s.is_final, s.token_name)
        if kind not in kinds:
            kinds[kind] = len(kinds)
        block[s] = kinds[kind]

    # keep splitting blocks until nothing changes
    while True:

        signatures = {}
        new_block = {}

        for s in states:

            targets = []
            for group in alphabet:
                target = move(s, group)
                targets.append(block[target] if target is not None else None)

            signature = (block[s], tuple(targets))      # my block + the blocks I lead to

            if signature not in signatures:
                signatures[signature] = len(signatures)
            new_block[s] = signatures[signature]

        done = len(signatures) == len(set(block.values()))
        block = new_block

        if done:
            break

    # build one new state per block
    new_states = {}
    members = {}

    for s in states:

        b = block[s]

        if b not in new_states:
            new_states[b] = State(f"M{len(new_states)}", [])
            new_states[b].is_final = s.is_final
            new_states[b].token_name = s.token_name
            members[b] = []

        members[b].append(s)

    new_states[block[start]].is_start = True

    table = []

    for b, newState in new_states.items():

        merged = {}                                     # target block -> characters leading there

        for chars, nextState in members[b][0].transitions:
            t = block[nextState]
            merged[t] = merged.get(t, "") + "".join(c for c in chars if c not in merged.get(t, ""))

        row = {"state": newState.name,
               "old states": "{" + ", ".join(s.name for s in members[b]) + "}",
               "arrows": [],
               "final": newState.token_name}

        for t, chars in merged.items():
            newState.add_transition(chars, new_states[t])
            row["arrows"].append((chars, new_states[t].name))

        table.append(row)

    return new_states[block[start]], table

def build_machine(tokens):


    nfa = remove_epsilon(union(tokens))
    dfa, table = subset_diviser(nfa, tokens)
    mini, mini_table = minimize(dfa)

    return mini

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
                
                print (f"{currentState.name} Is Final! --> {currentState.token_name}")




if __name__ == "__main__":

    TOKENS = [IF, SKIP, ELSE, ID]
    
    mini = build_machine(TOKENS)

    for t in tokenize(mini, code, TOKENS):
        print(t)