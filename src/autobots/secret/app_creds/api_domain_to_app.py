from src.autobots.secret.app_types import AppTypes

API_DOMAIN_TO_APP = {
    # slack
    "slack.com": AppTypes.slack.value,
    # google
    "googleapis.com": AppTypes.google.value,
    # jira
    "atlassian.net": AppTypes.jira.value,
    # zendesk
    "zendesk.com": AppTypes.zendesk.value,
    # zoho
    "zohoapis.ca": AppTypes.zoho.value,
    "zohoapis.eu": AppTypes.zoho.value,
    "zohoapis.com.cn": AppTypes.zoho.value,
    "zohoapis.com": AppTypes.zoho.value,
    "zohoapis.com.au": AppTypes.zoho.value,
    "zohoapis.in": AppTypes.zoho.value,
    "zohoapis.jp": AppTypes.zoho.value,
}
