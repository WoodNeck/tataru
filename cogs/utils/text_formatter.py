def strike(text):
    return "~~{}~~".format(text)


def underline(text):
    return "__{}__".format(text)


def bold(text):
    return "**{}**".format(text)


def italics(text):
    return "*{}*".format(text)


def inline(text):
    return "`{}`".format(text)


def box(lang, text):
    return "```{}\n{}```".format(lang, text)
