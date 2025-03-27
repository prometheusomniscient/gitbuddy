import requests
from requests.auth import HTTPBasicAuth

def create_jira_ticket(base_url, username, api_token, project_key, issue_type, summary, description):
    """
    Create a Jira ticket based on the provided criteria.

    Args:
        base_url (str): The base URL of the Jira instance (e.g., "https://yourdomain.atlassian.net").
        username (str): The Jira username or email address.
        api_token (str): The Jira API token for authentication.
        project_key (str): The key of the Jira project (e.g., "PROJ").
        issue_type (str): The type of the issue (e.g., "Bug", "Task").
        summary (str): The summary of the issue.
        description (str): The description of the issue.

    Returns:
        dict: The response from the Jira API, i ncluding the ticket key  and URL if successful.
    """
    url = f"{base_url}/rest/api/3/issue"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": issue_type
            }
        }
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            auth=HTTPBasicAuth(username, api_token)
        )

        if response.status_code == 201:
            ticket = response.json()
            print(f"Ticket created successfully: {ticket['key']}")
            return {
                "key": ticket["key"],
                "url": f"{base_url}/browse/{ticket['key']}"
            }
        else:
            print(f"Failed to create ticket: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error creating Jira ticket: {e}")
        return None
    
# Jira credentials and details
base_url = "https://yourdomain.atlassian.net"
username = "your-email@example.com"
api_token = "your_api_token"
project_key = "PROJ"
issue_type = "Task"
summary = "Implement new feature for user authentication"
description = "This task involves implementing a new feature for user authentication, including unit tests and documentation."

# Create the Jira ticket
ticket = create_jira_ticket(base_url, username, api_token, project_key, issue_type, summary, description)

if ticket:
    print(f"Ticket URL: {ticket['url']}")
