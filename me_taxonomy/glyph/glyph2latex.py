
def get_latex_by_glyph(glyph_name):
    from pdfxml.InftyCDB.name2latex import name2latex

    if glyph_name.startswith("\\mathcal") or glyph_name.startswith("mathcal"):
        return glyph_name[glyph_name.index("{")+1:glyph_name.index("}")]

    if glyph_name in name2latex:
        return name2latex[glyph_name]
    if glyph_name.startswith("not") and "\\" in glyph_name:
        return "\\"+glyph_name
    if glyph_name.startswith("\\"):
        return glyph_name

    if glyph_name in [' ', '?', '', '||']:
        return glyph_name

    raise Exception("TODO for glyph_name '{}'".format(glyph_name))
