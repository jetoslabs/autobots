from src.autobots.secret.app_creds.apps_enum import APPS_ENUM

API_DOMAIN_TO_APP = {
    # slack
    "slack.com": APPS_ENUM.slack.value,
    # google
    "googleapis.com": APPS_ENUM.google.value,
    # jira
    "atlassian.net": APPS_ENUM.jira.value,
    # zendesk
    "zendesk.com": APPS_ENUM.zendesk.value,
    # zoho
    "zohoapis.ca": APPS_ENUM.zoho.value,
    "zohoapis.eu": APPS_ENUM.zoho.value,
    "zohoapis.com.cn": APPS_ENUM.zoho.value,
    "zohoapis.com": APPS_ENUM.zoho.value,
    "zohoapis.com.au": APPS_ENUM.zoho.value,
    "zohoapis.in": APPS_ENUM.zoho.value,
    "zohoapis.jp": APPS_ENUM.zoho.value,
}
