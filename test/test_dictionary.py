from dictionary import get_definition, summarise


def test_get_definition():
    word = "apple"
    definition = get_definition(word)
    assert definition is not None
    assert isinstance(definition, str)


def test_get_definition_not_found():
    word = "no such word"
    definition = get_definition(word)
    assert definition is None


def test_summarise():
    long_definition = """1. A massive, compact limestone; a variety of calcite, capable of being polished and used for architectural and ornamental purposes. The color varies from white to black, being sometimes yellow, red, and green, and frequently beautifully veined or clouded. The name is also given to other rocks of like use and appearance, as serpentine or verd antique marble, and less properly to polished porphyry, granite, etc. Note: Breccia marble consists of limestone fragments cemented together. -- Ruin marble, when polished, shows forms resembling ruins, due to disseminated iron oxide. -- Shell marble contains fossil shells. -- Statuary marble is a pure, white, fine-grained kind, including Parian (from Paros) and Carrara marble. If coarsely granular it is called saccharoidal. 2. A thing made of, or resembling, marble, as a work of art, or record, in marble; or, in the plural, a collection of such works; as, the Arundel or Arundelian marbles; the Elgin marbles. 3. A little ball of marble, or of some other hard substance, used as a plaything by children; or, in the plural, a child's game played with marbles. Note: Marble is also much used in self-explaining compounds; when used figuratively in compounds it commonly means, hard, cold, destitute of compassion or feeling; as, marble-breasted, marble- faced, marble-hearted.

1. Made of, or resembling, marble; as, a marble mantel; marble paper. 2. Cold; hard; unfeeling; as, a marble breast or heart.

To stain or vein like marble; to variegate in color; as, to marble the edges of a book, or the surface of paper."""
    summary = """1. A massive, compact limestone; a variety of calcite, capable of being polished and used for archit...

1. Made of, or resembling, marble; as, a marble mantel; marble paper. 2. Cold; hard; unfeeling; as, ...

To stain or vein like marble; to variegate in color; as, to marble the edges of a book, or the surfa..."""
    assert summarise(long_definition) == summary
