"""
Original: https://github.com/choldgraf/choldgraf.github.io/blob/main/scripts/orcid-publications.py
"""
import argparse
import json
from pathlib import Path

import pandas as pd
import requests
from rich import progress

# My ORCID
ORCID_ID = "0000-0001-8833-7617"
LASTNAME = "Webel"
ORCID_RECORD_API = "https://pub.orcid.org/v3.0/"

# Download all of my ORCID records
print("Retrieving ORCID entries from API...")
response = requests.get(
    url=requests.utils.requote_uri(ORCID_RECORD_API + ORCID_ID),
    headers={"Accept": "application/json"},
)
response.raise_for_status()
orcid_record = response.json()


##
# Resolve DOIs from ORCID as references
# Shamelessly copied from:
# https://gist.github.com/brews/8d3b3ede15d120a86a6bd6fc43859c5e


def fetchmeta(doi, fmt="reference", **kwargs):
    """Fetch metadata for a given DOI.

    Parameters
    ----------
    doi : str
    fmt : str, optional
        Desired metadata format. Can be 'dict' or 'bibtex'.
        Default is 'dict'.
    **kwargs :
        Additional keyword arguments are passed to `json.loads()` if `fmt`
        is 'dict' and you're a big JSON nerd.

    Returns
    -------
    out : str or dict or None
        `None` is returned if the server gives unhappy response. Usually
        this means the DOI is bad.

    Examples
    --------
    >>> fetchmeta('10.1016/j.dendro.2018.02.005')
    >>> fetchmeta('10.1016/j.dendro.2018.02.005', 'bibtex')

    References
    ----------
    https://www.doi.org/hb.html
    """
    # Parse args and setup the server response we want.
    accept_type = "application/"
    if fmt == "dict":
        accept_type += "citeproc+json"
    elif fmt == "bibtex":
        accept_type += "x-bibtex"
    elif fmt == "reference":
        accept_type = "text/x-bibliography; style=apa"
    else:
        raise ValueError(f"Unrecognized `fmt`: {fmt}")

    # Request data from server.
    url = "https://dx.doi.org/" + str(doi)
    header = {"accept": accept_type}
    r = requests.get(url, headers=header)

    # Format metadata if server response is good.
    out = None
    if r.status_code == 200:
        if fmt == "dict":
            out = json.loads(r.text, **kwargs)
        else:
            out = r.text
    return out


# Extract metadata for each entry
df = []
for iwork in progress.track(
    orcid_record["activities-summary"]["works"]["group"], "Fetching reference data..."
):
    isummary = iwork["work-summary"][0]

    # Extract the DOI
    for ii in isummary["external-ids"]["external-id"]:
        if ii["external-id-type"] == "doi":
            doi = ii["external-id-value"]
            break

    meta = fetchmeta(doi, fmt="dict")
    doi_url = meta["URL"]
    title = meta["title"]
    references_count = meta["references-count"]
    year = meta["issued"]["date-parts"][0][0]
    url = meta["URL"]

    # Create authors list with links to their ORCIDs
    authors = meta["author"]
    autht = []
    for author in authors:
        try:
            name = f"{author['family']}, {author['given'][0]}."
            if LASTNAME.lower() in author["family"].lower():
                name = f"**{name}**"
            if "ORCID" in author:
                name = f"[{name}]({author['ORCID']})"
        except KeyError:
            # incase family and given names are not available (e.g. consortiums)
            name = author["name"]
        autht.append(name)
    autht = ", ".join(autht)

    journal = meta["publisher"]

    url_doi = url.split("//", 1)[-1]
    reference = f"{autht} ({year}). **{title}**. {journal}. [{url_doi}]({url})"
    df.append({"year": year, "reference": reference})
df = pd.DataFrame(df)

# Convert into a markdown string
md = []
for year, items in df.groupby("year", sort=False):
    md.append(f"## {year}")
    for _, item in items.iterrows():
        md.append(item["reference"])
        md.append("")
    md.append("")
mds = "\n".join(md)

# path_out = Path(__file__).parent.parent / "_static/publications.txt"
path_out = Path("publications.md").absolute()
# fix encoding to support special characters:
path_out.write_text(mds, encoding="utf-8")
print(f"Finished updating ORCID entries at: {path_out}")

