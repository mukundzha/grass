from grass import search


def make_state(lines, cy, cx, term):
    state = {
        "lines": lines,
        "cy": cy,
        "cx": cx,
        "search_term": term,
        "matches": [],
        "search_version": -1,
        "message": "",
        "version": 0,
    }
    return state


def test_update_matches_finds_all_occurrences():
    state = make_state(["foo foo", "bar", "foo"], 0, 0, "foo")
    search.update_matches(state)
    assert state["matches"] == [(0, 0, 3), (0, 4, 3), (2, 0, 3)]


def test_update_matches_skips_when_version_unchanged():
    state = make_state(["foo"], 0, 0, "foo")
    search.update_matches(state)
    assert len(state["matches"]) == 1
    state["matches"] = []
    search.update_matches(state)
    assert state["matches"] == []


def test_find_next_moves_forward():
    state = make_state(["foo", "foo"], 0, 0, "foo")
    search.find_next(state)
    assert state["cy"] == 1
    assert state["cx"] == 0
    assert state["message"] == "Match 2 of 2"


def test_find_next_wraps_to_first():
    state = make_state(["foo", "foo"], 1, 0, "foo")
    search.find_next(state)
    assert state["cy"] == 0
    assert state["cx"] == 0
    assert state["message"] == "Match 1 of 2"


def test_find_next_not_found():
    state = make_state(["bar"], 0, 0, "foo")
    search.find_next(state)
    assert state["message"] == "Not found: foo"


def test_update_matches_refreshes_after_edit():
    state = make_state(["foo"], 0, 0, "foo")
    search.update_matches(state)
    assert len(state["matches"]) == 1
    state["lines"] = ["bar"]
    state["version"] = 1
    search.update_matches(state)
    assert len(state["matches"]) == 0
