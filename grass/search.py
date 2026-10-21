def update_matches(state):
    if state["search_version"] == state["version"]:
        return
    matches = []
    term = state["search_term"]
    if term != "":
        line_index = 0
        for line in state["lines"]:
            position = line.find(term)
            while position != -1:
                matches.append((line_index, position, len(term)))
                position = line.find(term, position + len(term))
            line_index = line_index + 1
    state["matches"] = matches
    state["search_version"] = state["version"]


def index_at_cursor(state):
    index = 0
    for match in state["matches"]:
        if match[0] == state["cy"] and match[1] == state["cx"]:
            return index
        index = index + 1
    return -1


def first_match_index(matches, cy, cx):
    index = 0
    for match in matches:
        line = match[0]
        start = match[1]
        if line > cy:
            return index
        if line == cy and start >= cx:
            return index
        index = index + 1
    return 0


def find_next(state):
    update_matches(state)
    matches = state["matches"]
    if len(matches) == 0:
        state["message"] = "Not found: " + state["search_term"]
        return
    target = None
    index = 0
    while index < len(matches):
        match = matches[index]
        line = match[0]
        start = match[1]
        after = False
        if line > state["cy"]:
            after = True
        if line == state["cy"] and start > state["cx"]:
            after = True
        if after:
            target = match
            break
        index = index + 1
    if target is None:
        target = matches[0]
        index = 0
    state["cy"] = target[0]
    state["cx"] = target[1]
    state["message"] = "Match " + str(index + 1) + " of " + str(len(matches))
