"""
Original: https://github.com/choldgraf/choldgraf.github.io/blob/main/scripts/orcid-publications.py
"""

import argparse
from pathlib import Path

import pandas as pd
import requests
from rich import progress

from .query import fetchmeta

ORCID_RECORD_API = "https://pub.orcid.org/v3.0/"


def main():
    parser = argparse.ArgumentParser(description="Retrieve and process ORCID entries")
    parser.add_argument("--orcid-id", type=str, help="ORCID ID")
    parser.add_argument("--lastname", type=str, help="Last name")
    parser.add_argument("--output-file", type=str, help="Output file path")
    args = parser.parse_args()

    # Set ORCID ID and last name
    ORCID_ID = args.orcid_id
    LASTNAME = args.lastname

    # Download all of the ORCID records
    print("Retrieving ORCID entries from API...")
    response = requests.get(
        url=requests.utils.requote_uri(ORCID_RECORD_API + ORCID_ID),
        headers={"Accept": "application/json"},
    )
    response.raise_for_status()
    orcid_record = response.json()

    # Resolve DOIs from ORCID as references
    df = []
    for iwork in progress.track(
        orcid_record["activities-summary"]["works"]["group"],
        "Fetching reference data...",
    ):
        isummary = iwork["work-summary"][0]

        # Extract the DOI
        for ii in isummary["external-ids"]["external-id"]:
            if ii["external-id-type"] == "doi":
                doi = ii["external-id-value"]
                break

        meta = fetchmeta(doi, fmt="dict")
        # doi_url = meta["URL"]
        title = meta["title"]
        # references_count = meta["references-count"]
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

    # Write to output file
    path_out = Path(args.output_file).absolute()
    path_out.write_text(mds, encoding="utf-8")
    print(f"Finished updating ORCID entries at: {path_out}")


if __name__ == "__main__":
    main()
