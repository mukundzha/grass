TAB_WIDTH = 4


def display_column(text, index):
    if index > len(text):
        index = len(text)
    column = 0
    position = 0
    while position < index:
        if text[position] == "\t":
            column = column + TAB_WIDTH - (column % TAB_WIDTH)
        else:
            column = column + 1
        position = position + 1
    return column


def expand_tabs(text):
    result = ""
    column = 0
    for character in text:
        if character == "\t":
            spaces = TAB_WIDTH - (column % TAB_WIDTH)
            result = result + " " * spaces
            column = column + spaces
        else:
            result = result + character
            column = column + 1
    return result


def char_index_at_column(text, target):
    column = 0
    index = 0
    while index < len(text):
        if text[index] == "\t":
            next_column = column + TAB_WIDTH - (column % TAB_WIDTH)
        else:
            next_column = column + 1
        if next_column > target:
            break
        column = next_column
        index = index + 1
    return index
