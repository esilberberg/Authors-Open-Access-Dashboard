# The Open Access Dashboard

## Overview
The Open Access Dashboard is a Streamlit web app that helps researchers understand the open access (OA) status of their publications.

By entering an ORCID ID, the app retrieves a list of the user's scholarly works and provides an analysis of their open access status. The dashboard helps you quickly see which of your papers are open and, for those that aren't, offers pathways to make them so.

## How it works
The core of this project is a Python script, `build_articles_oa_overview.py`, which performs the following steps:

- **Retrieves Author Publications:** The script uses an author's ORCID to query the ORCID API and collect a list of their published works and associated DOIs.
- **Determines Open Access Status:** For each publication with a DOI (it must have a DOI to be processed by the script), the script queries the Unpaywall API using the article's DOI to determine its current open access status.
- **Retrieves Journal Policies:** The script also uses the JISC Open Policy Finder API to fetch the green open access policies (e.g., fees, embargo periods, permitted repositories) for the journals in which articles have been published.
- **Generates a Report:** All collected data is compiled into a pandas DataFrame, providing a clear and structured overview.

## Dependencies
<p>
<img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit Badge">
</p>
<p>
<img src="https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas Badge">
</p>
JISC Open Policy Finder API key as a Streamlit secret in `.streamlit/secrets.toml`

## Limitations
Articles without a valid DOI cannot be checked for OA status or journal policies. The accuracy of the output is dependent on the data provided by ORCID, Unpaywall, and JISC Open Policy Finder.
