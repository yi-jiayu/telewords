from dictionary import get_definition


def test_get_definition():
    word = "apple"
    definition = get_definition(word)
    assert definition is not None
    assert isinstance(definition, str)


def test_get_definition_not_found():
    word = "no such word"
    definition = get_definition(word)
    assert definition is None
