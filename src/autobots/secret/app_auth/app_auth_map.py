from src.autobots.secret.app_auth.app_auth_type.jira_auth import JiraAuth
from src.autobots.secret.app_auth.app_auth_type.slack_auth import SlackAuth
from src.autobots.secret.app_auth.app_auth_type.zendesk_auth import ZendeskAuth
from src.autobots.secret.app_auth.app_auth_type.zoho_auth import ZohoAuth
from src.autobots.secret.app_auth.app_auths_enum import APP_AUTHS

APP_AUTH_MAP = {
    APP_AUTHS.jira.value: JiraAuth,
    APP_AUTHS.slack.value: SlackAuth,
    APP_AUTHS.zoho.value: ZohoAuth,
    APP_AUTHS.zendesk.value: ZendeskAuth,
}
