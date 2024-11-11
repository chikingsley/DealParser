Notion Integration Instructions for Deal Submission Bot

Overview: This bot will send confirmed deals to a Notion database when the user presses the “Submit to Notion” button. The integration will involve adding new entries with specific properties, as well as managing relational links to a separate “⚡ ALL ADVERTISERS | Kitchen” database.

Requirements

	•	Main Database ID: 11b0e6159a9080e39356fa80451493b9
	•	Kitchen Database ID: 11b0e6159a9080ce8fcdf3d53053cf31
	•	Notion Token: ntn_B38601755044rj0V1HhNCj6PwPQyuau8U8VCSgTjVaTemE
	•	API Endpoint: https://api.notion.com/v1/pages for creating pages.

Steps to Implement

1. Set Up Notion API Authorization

	•	Use the NOTION_TOKEN for authenticating requests.
	•	Add Authorization: Bearer ntn_B38601755044rj0V1HhNCj6PwPQyuau8U8VCSgTjVaTemE in the headers for each API call.

2. Data Preparation and Formatting

Define Each Field Value as Follows:
	•	Geo-Funnel Code: GEO Codes + " " + Languages (separated by "|") + "-" + Partner/Company Name + "-" + Sources (separated by "|").
	•	Deal Status: Set to "Active".
	•	Funnels: Comma-separated list of funnels.
	•	Language: Comma-separated list of languages.
	•	Sources: Comma-separated list of sources.
	•	CPA | Buying: Set to the confirmed CPA value.
	•	CRG | Buying: Confirmed CRG value in decimal form (e.g., 13% becomes 0.13).
	•	CPL | Buying: Set to the confirmed CPL value.
	•	CPA | Network: CPA + 100.
	•	CRG | Network: CRG + 1 in decimal form (e.g., 13% + 1 = 14% becomes 0.14).
	•	CPL | Network: CPL + 5.
	•	Deduction %: Deduction limit in decimal form (e.g., 5% becomes 0.05).
	•	⚡ ALL ADVERTISERS | Kitchen: Relational field to link to the company/partner in the “Kitchen” database.

3. Set up the Logic to Handle the “⚡ ALL ADVERTISERS | Kitchen” Relation

	•	Check for Existing Company Entry:
	•	Query the “⚡ ALL ADVERTISERS | Kitchen” database (ID: 11b0e6159a9080ce8fcdf3d53053cf31) for a page with the Partner/Company Name.
	•	If found, retrieve the page ID to use in the relation.
	•	Create New Entry if Company Doesn’t Exist:
	•	If the Partner/Company Name isn’t found, create a new page in the “⚡ ALL ADVERTISERS | Kitchen” database with this name as the title.
	•	Retrieve the new page ID for linking.

4. API Call to Create a New Deal Entry

	•	Use the create page endpoint (https://api.notion.com/v1/pages) to submit the formatted fields to the main database.
	•	Pass the database ID, parent reference, and formatted properties for each required field.

5. Example Code for Creating and Submitting a Deal Entry

from notion_client import Client

# Initialize Notion Client
notion = Client(auth="ntn_B38601755044rj0V1HhNCj6PwPQyuau8U8VCSgTjVaTemE")

# Main function to create a deal entry
def add_deal(database_id, kitchen_database_id, deal_data):
    # Function to check or create a company entry in the Kitchen database
    company_id = get_or_create_company(kitchen_database_id, deal_data["company_name"])

    # Define properties based on provided deal data
    properties = {
        "Geo-Funnel Code": {
            "title": [{"text": {"content": f"{deal_data['geo']}|{deal_data['language']} - {deal_data['company_name']} - {deal_data['sources']}"}}]
        },
        "Deal Status": {"select": {"name": "Active"}},
        "Funnels": {"multi_select": [{"name": funnel} for funnel in deal_data["funnels"].split(",")]},
        "Language": {"multi_select": [{"name": lang} for lang in deal_data["language"].split(",")]},
        "Sources": {"multi_select": [{"name": source} for source in deal_data["sources"].split(",")]},
        "CPA | Buying": {"number": deal_data["cpa_buying"]},
        "CRG | Buying": {"number": deal_data["crg_buying"]},
        "CPL | Buying": {"number": deal_data["cpl_buying"]},
        "CPA | Network": {"number": deal_data["cpa_buying"] + 100},
        "CRG | Network": {"number": deal_data["crg_buying"] + 1},
        "CPL | Network": {"number": deal_data["cpl_buying"] + 5},
        "Deduction %": {"number": deal_data["deduction"]},
        "⚡ ALL ADVERTISERS | Kitchen": {"relation": [{"id": company_id}]}
    }

    # Create the new page
    new_page = notion.pages.create(parent={"database_id": database_id}, properties=properties)
    return new_page

# Helper function to get or create a company in the Kitchen database
def get_or_create_company(kitchen_database_id, company_name):
    # Search for existing company
    search_results = notion.databases.query(
        database_id=kitchen_database_id,
        filter={"property": "Name", "text": {"equals": company_name}}
    )
    if search_results["results"]:
        return search_results["results"][0]["id"]
    else:
        new_company = notion.pages.create(
            parent={"database_id": kitchen_database_id},
            properties={"Name": {"title": [{"text": {"content": company_name}}]}}
        )
        return new_company["id"]

6. Error Handling and Testing

	•	Test Cases:
	•	Verify functionality with cases where the company exists and where it doesn’t.
	•	Confirm that all fields populate correctly and relations are handled.
	•	API Limits and Errors:
	•	Handle API rate limits gracefully.
	•	Log any failed requests for debugging.

Final Notes

	•	Field Structure: Ensure all fields match the database schema exactly, especially multi-selects and relations.
	•	Testing: Confirm that company/partner entries populate correctly and are accessible for future updates or linking.

This setup should allow for efficient deal entry submission and smooth linking to the “⚡ ALL ADVERTISERS | Kitchen” database. 