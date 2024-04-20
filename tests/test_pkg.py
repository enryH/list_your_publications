import orcidpubs


def test_version_tag():
    _ = orcidpubs.__version__


def test_fetchmeta():
    doi = "10.1016/j.dendro.2018.02.005"
    meta = orcidpubs.query.fetchmeta(doi, fmt="dict")
    assert meta["title"] == "burnr: Fire history analysis and graphics in R"
    assert orcidpubs.query.fetchmeta(doi) == (
        "Malevich, S. B., Guiterman, C. H., & Margolis, E. Q. (2018)."
        " burnr: Fire history analysis and graphics in R. Dendrochronologia, 49,"
        " 9â\x80\x9315. https://doi.org/10.1016/j.dendro.2018.02.005\n"
    )
