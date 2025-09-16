import streamlit as st
import re
from build_articles_oa_overview import build_articles_oa_overview

st.set_page_config(page_title="Open Access Dashboard", page_icon=":unlock:", layout="centered", initial_sidebar_state="expanded")
with st.sidebar:
    st.header(":mag_right: Glossary")
    st.markdown('''
    - **Published Version**: The final, typeset pdf as it appears in the journal.
    - **Accepted Version**: After peer review, but before the journal has formatted it for publication. Usually a Word document.
    - **Submitted Versions**: Also called a preprint, the draft an author initially submits to a journal. Usually a Word document.
    ''')
    with st.expander(":books: **Get Started**"):
        st.markdown("""
        The Open Access Dashboard retrieves a list of your publications and determines their open access (OA) status. For publications that are :warning: **Closed Access**, we provide several pathways to make them open. 
        
        Each pathway has its own rules. For example, you might pay a fee to immediately make the final, **Published Version** of your article OA. 
        
        Alternatively, you might make the **Accepted Version** of your article (the version after peer review but before the publisher's final formatting) available in a repository like [CUNY Academic Works](https://academicworks.cuny.edu/). This option is often free but may require you to wait for a specific time period, known as an **embargo**.
        """)
    with st.expander(":bar_chart: **Data Sources**"):
        st.markdown("This dashboard uses data from ORCID, Unpaywall, and the JISC Open Policy Finder. For your publications to be processed, they must be on your ORCID record and include a DOI.")
    
st.title(":unlock: Open Access Dashboard")
orcid_input = st.text_input("ORCID:")


if orcid_input:
    # ORCID validation
    orcid_pattern = r'^[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}$'
    if not re.match(orcid_pattern, orcid_input):
        st.error("Invalid ORCID format. Please use the format XXXX-XXXX-XXXX-XXXX.")
        st.stop()

    # Get the JISC API key from secrets
    jisc_api_key = st.secrets["api-jisc"]
    st.write(f"API Key loaded (first 5 chars): {jisc_api_key[:5]}...")

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

                # # Display journal permissions inside the container
                journal_permissions = row['Journal Permissions']
                journal_permissions.reverse()

                if row['OA Status'] is False:  
                    if journal_permissions:
                        st.markdown("**How to Make This Open Access:**")
                        for perm in journal_permissions:
                            
                            #Logic for oa options panels
                            if perm['additional_oa_fee'] =='Yes':
                                oa_fee_txt = "A fee is required."
                            else:
                                oa_fee_txt = "No fee required."
                            
                            if perm['embargo_period'] == 'None':
                                embargo_txt = "You can make it open access immediately."
                            else:
                                embargo_txt = f"You can make it open access after an embargo period of {perm['embargo_period']}."

                            if perm['deposit_locations'] != 'None':
                                location_txt = f"**Where you can deposit it:** {perm['deposit_locations']}."
                            else: 
                                location_txt = 'No specific deposit locations mentioned.'

                            if perm['named_repositories'] != 'None':
                                named_repo_txt = f"**Permitted repositories:** {perm['named_repositories']}."
                            else:
                                named_repo_txt = ''
                            
                            with st.expander(f"**{perm['version']} Version**"):
                                
                                details = []
                                details.append(f"- **Cost:** {oa_fee_txt}")
                                details.append(f"- **Embargo:** {embargo_txt}")
                                if location_txt and location_txt != 'No specific deposit locations mentioned.':
                                    details.append(f"- {location_txt}")
                                if named_repo_txt:
                                    details.append(f"- {named_repo_txt}")
                            
                                final_text = "\n".join(details)
                                st.write(final_text)
                    else:
                        st.markdown("*No open access options found.*")
                else:
                    st.markdown("")
                    
    else:
        st.error("*No publications found for the provided ORCID.*")