import streamlit as st
import re
from build_articles_oa_overview import build_articles_oa_overview

st.set_page_config(page_title="Open Access Dashboard", page_icon=":unlock:", layout="centered", initial_sidebar_state="expanded")
with st.sidebar:
    st.header(":books: About")
    st.markdown("The Open Access Dashboard retrieves a list of your scholarly publications and analyzes their open access (OA) status. For each publication with a DOI, it tells you whether the article is currently open access or provides options for making closed-access publications open. All data is sourced from ORCID, Unpaywall, and the JISC Open Policy Finder.")
    st.header(":mag_right: Glossary")
    st.markdown('''
    - **Published Version**: The final, typeset article as it appears in the journal, with the official publication date.  
    - **Accepted Version**: The final manuscript after peer review, but before the journal has formatted it for publication. Usually a Word document.
    - **Submitted Versions**: The first draft of an article, also called a preprint, that an author submits to a journal for review. Usually a Word document.
    ''')
st.title(":unlock: Open Access Dashboard")
orcid_input = st.text_input("Enter your ORCID:")


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
        st.header(f"{data.iloc[0]['Author']}'s Publications")
        
        oa_status_options = ["All", "Open Access", "Closed Access"]
        oa_status_selection = st.segmented_control(
        "View publications by open access status:", oa_status_options, selection_mode="single", default="All")
        if oa_status_selection == "Open Access":
            data = data[data['OA Status'] == True]
        elif oa_status_selection == "Closed Access":
            data = data[data['OA Status'] == False]
        
        #Blank space
        st.markdown('####')
        
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