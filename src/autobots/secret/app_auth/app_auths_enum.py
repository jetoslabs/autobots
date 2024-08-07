from enum import Enum


class ExtendedEnum(Enum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def set(cls):
        return set(map(lambda c: c.value, cls))


class APP_AUTHS(ExtendedEnum):
    jira = "jira"
    slack = "slack"
    zoho = "zoho"
    zendesk = "zendesk"
