from src.autobots.secret.app_creds.app_creds_type.google_creds import GoogleCreds
from src.autobots.secret.app_creds.app_creds_type.jira_creds import JiraCreds
from src.autobots.secret.app_creds.app_creds_type.slack_creds import SlackCreds
from src.autobots.secret.app_creds.app_creds_type.zendesk_creds import ZendeskCreds
from src.autobots.secret.app_creds.app_creds_type.zoho_creds import ZohoCreds

from src.autobots.secret.app_types import AppTypes


AppTypeToAppCredsClass = {
    AppTypes.google: GoogleCreds,
    AppTypes.jira: JiraCreds,
    AppTypes.slack: SlackCreds,
    AppTypes.zendesk: ZendeskCreds,
    AppTypes.zoho: ZohoCreds,
}
