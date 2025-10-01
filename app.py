import streamlit as st
import pandas as pd
import re
from build_articles_oa_overview import build_articles_oa_overview

def get_composite_permissions(permissions_list):
    """
    Groups permissions by version and creates a composite view for each.
    
    Returns a dictionary where keys are version names and values are
    composite details.
    """
    composite_data = {}

    for perm in permissions_list:
        version = perm['version']

        if version not in composite_data:
            composite_data[version] = {
                'oa_fee_required': False,
                'longest_embargo': 0,
                'deposit_locations': set(),
                'named_repositories': set()
            }

        # Check for OA fee
        if perm['additional_oa_fee'] == 'Yes':
            composite_data[version]['oa_fee_required'] = True
        
        # Find the longest embargo period
        embargo_str = perm['embargo_period']
        if embargo_str != 'None':
            months = int(embargo_str.split()[0])
            if months > composite_data[version]['longest_embargo']:
                composite_data[version]['longest_embargo'] = months

        # Collect unique deposit locations and named repositories
        if perm['deposit_locations'] != 'None':
            # Split the string and add each location individually to the set
            locations = [loc.strip() for loc in perm['deposit_locations'].split(',')]
            for loc in locations:
                if loc:  # Ensure no empty strings are added
                    composite_data[version]['deposit_locations'].add(loc)
                    
        if perm['named_repositories'] != 'None':
            composite_data[version]['named_repositories'].add(perm['named_repositories'])

    return composite_data

st.set_page_config(page_title="Open Access Dashboard", page_icon=":unlock:", layout="centered", initial_sidebar_state="expanded")
with st.sidebar:
    st.header(":mag_right: Glossary")
    st.markdown('''
    - **Published Version**: The final, typeset PDF as it appears in the journal.
    - **Accepted Version**: Peer-reviewed and accepted by a journal, but not yet typeset for publication.
    - **Submitted**: The draft you initially submit to a journal. 
    ''')

    st.divider()
    st.markdown('''
    ### :zap: Maximize Your Impact!
    
    Once you find an OA pathway for your work (e.g., **Accepted Version**), **upload it to [CUNY Academic Works](https://academicworks.cuny.edu/)** to promote wider readership.
    ''')
    st.image("media/caw-logo.png", width="stretch")


    st.divider()    
    with st.expander(":books: **About**"):
        st.markdown("""
        The Open Access Dashboard retrieves a list of your publications and determines their open access (OA) status. For publications that are :warning: **Closed Access**, we provide several pathways to make them open. 
        
        Each pathway has its own rules. For example, you might pay a fee to immediately make the final, **Published Version** of your article OA. 
        
        Alternatively, you might make the **Accepted Version** of your article (the version after peer review but before the publisher's final formatting) available in a repository like [CUNY Academic Works](https://academicworks.cuny.edu/). This option is often free but may require you to wait for a specific time period, known as an **embargo**.
        """)
    with st.expander(":bar_chart: **Data Sources**"):
        st.markdown("This dashboard uses data from ORCID, Unpaywall, and the JISC Open Policy Finder. For your publications to be processed, they must be on your ORCID record and include a DOI.")
    
st.title(":unlock: Open Access Dashboard")
orcid_input = st.text_input("Input your ORCID:")

if orcid_input:
    # ORCID validation
    orcid_pattern = r'^[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}$'
    if not re.match(orcid_pattern, orcid_input):
        st.error("Invalid ORCID format. Please use the format XXXX-XXXX-XXXX-XXXX.")
        st.stop()

    # Get the JISC API key from secrets
    jisc_api_key = st.secrets["api-jisc"]

    # Spinner to show while fetching data
    with st.spinner('Loading...'):
        data = build_articles_oa_overview(orcid_input, jisc_api_key)

    if not data.empty:
        st.header(f"{data.iloc[0]['Author']}")
        
        oa_status_options = ["All", "Open Access", "Closed Access"]
        oa_status_selection = st.segmented_control(
        "View publications by open access status:", oa_status_options, selection_mode="single", default="All")
        number_of_publications = len(data)
        if oa_status_selection == "Open Access":
            data = data[data['OA Status'] == True]
            number_of_publications = len(data)
        elif oa_status_selection == "Closed Access":
            data = data[data['OA Status'] == False]
            number_of_publications = len(data)
        
        st.markdown(f"### {number_of_publications} Publication{'s' if number_of_publications != 1 else ''}")
       
        # Blank space
        st.markdown('#####')
        
        for index, row in data.iterrows():
            # A container for each publications
            with st.container(border=True):
            
                st.write()
                st.markdown(f"##### {row['Article']}")
            
                if row['OA Status']:
                    st.badge("Open Access", icon=":material/check:", color="green")
                else: 
                    st.badge("Closed Access", icon="⚠️", color="orange")

                if row['Journal'] != 'No journal':
                    journal_info = f"{row['Journal']}"
                else: journal_info = ''

                multi = f'''
                {journal_info}  
                {row['Year']}  |  {row['Publication Type']}  
                DOI: [{row['DOI']}](https://doi.org/{row['DOI']})
                ''' 
                st.markdown(multi)

                # Manage Journal OA permissions/policies
                journal_permissions = row['Journal Permissions']

                if row['OA Status'] is False:
                    if journal_permissions:
                        st.markdown("**How to Make This Open Access:**")
                        
                        composite_perms = get_composite_permissions(journal_permissions)
                        
                        # Set order of the expanders
                        version_order = ['Submitted', 'Accepted', 'Published']

                        for version_type in version_order:
                            if version_type in composite_perms:
                                composite = composite_perms[version_type]
                                
                                # Set the expander names
                                expander_title = f"**{version_type} Version**"
                                if version_type == "Submitted":
                                    expander_title = "**Submitted**"

                                with st.expander(expander_title):
                                    details = []
                                    
                                    # OA fee logic
                                    oa_fee_txt = "A fee is required." if composite['oa_fee_required'] else "No fee required."
                                    details.append(f"- **Cost:** {oa_fee_txt}")

                                    # Embargo period logic
                                    if composite['longest_embargo'] > 0:
                                        embargo_txt = f"You can make it open access after an embargo period of {composite['longest_embargo']} months."
                                    else:
                                        embargo_txt = "You can make it open access immediately."
                                    details.append(f"- **Embargo:** {embargo_txt}")
                                    
                                    # Deposit locations
                                    if composite['deposit_locations']:
                                        location_txt = ", ".join(composite['deposit_locations'])
                                        details.append(f"- **Where you can deposit it:** {location_txt}.")
                                    
                                    # Named repositories
                                    if composite['named_repositories']:
                                        named_repo_txt = ", ".join(composite['named_repositories'])
                                        details.append(f"- **Permitted repositories:** {named_repo_txt}.")

                                    final_text = "\n".join(details)
                                    st.write(final_text)

                    else:
                        st.markdown("*No open access options found.*")
                else:
                    st.markdown("")

    else:
        st.error("*No publications found for the provided ORCID.*")
