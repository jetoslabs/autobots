from enum import Enum


class ExtendedEnum(str, Enum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def set(cls):
        return set(map(lambda c: c.value, cls))


class AppTypes(ExtendedEnum):
    jira = "jira"
    slack = "slack"
    zoho = "zoho"
    zendesk = "zendesk"
    google = "google"
