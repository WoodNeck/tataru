def emphasis(word):
    return "**{}**".format(word)

def underline(word):
    return "__{}__".format(word)

def italics(word):
    return "*{}*".format(word)

def code(word):
    return "`{}`".format(word)

def block(word, lang):
    return "```{}\n{}```".format(lang, word)
