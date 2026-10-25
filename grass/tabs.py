import unicodedata

TAB_WIDTH = 4


def character_width(character):
    if character == "\t":
        return 1
    if unicodedata.combining(character) != 0:
        return 0
    category = unicodedata.category(character)
    if category == "Mn" or category == "Me" or category == "Cf":
        return 0
    east_asian = unicodedata.east_asian_width(character)
    if east_asian == "W" or east_asian == "F":
        return 2
    return 1


def display_width(text):
    column = 0
    for character in text:
        if character == "\t":
            column = column + TAB_WIDTH - (column % TAB_WIDTH)
        else:
            column = column + character_width(character)
    return column


def display_column(text, index):
    if index > len(text):
        index = len(text)
    column = 0
    position = 0
    while position < index:
        character = text[position]
        if character == "\t":
            column = column + TAB_WIDTH - (column % TAB_WIDTH)
        else:
            column = column + character_width(character)
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
            column = column + character_width(character)
    return result


def char_index_at_column(text, target):
    column = 0
    index = 0
    while index < len(text):
        character = text[index]
        if character == "\t":
            next_column = column + TAB_WIDTH - (column % TAB_WIDTH)
        else:
            next_column = column + character_width(character)
        if next_column > target:
            break
        column = next_column
        index = index + 1
    return index


def column_boundary(text, column):
    if column <= 0:
        return 0
    index = char_index_at_column(text, column)
    return display_column(text, index)


def text_in_columns(text, start, end):
    if end <= start:
        return ""
    result = ""
    column = 0
    for character in text:
        if character == "\t":
            width = TAB_WIDTH - (column % TAB_WIDTH)
            piece = " " * width
        else:
            width = character_width(character)
            piece = character
        next_column = column + width
        if width == 0:
            if column >= start and column <= end:
                result = result + piece
            column = next_column
            continue
        if next_column <= start:
            column = next_column
            continue
        if column >= end:
            break
        if column < start:
            if character == "\t":
                piece = piece[start - column:]
                next_column = start + len(piece)
                column = start
            else:
                piece = " " * (next_column - start)
                column = start
        if next_column > end:
            break
        result = result + piece
        column = next_column
    return result


def truncate_width(text, width):
    if width <= 0:
        return ""
    result = ""
    column = 0
    for character in text:
        if character == "\t":
            size = TAB_WIDTH - (column % TAB_WIDTH)
            piece = " " * size
        else:
            size = character_width(character)
            piece = character
        if size == 0:
            result = result + piece
            continue
        if column + size > width:
            break
        result = result + piece
        column = column + size
    return result
