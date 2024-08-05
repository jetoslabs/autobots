from typing import Type

from src.autobots.secret.app_creds.app_creds_model import ApiKeyCredsModel
from src.autobots.secret.app_creds.app_creds_type.app_creds_type import AppCredsType
from src.autobots.secret.app_creds.apps_enum import APPS_ENUM


class ZendeskCreds(AppCredsType):
    @staticmethod
    def get_app() -> APPS_ENUM:
        return APPS_ENUM.zendesk

    @staticmethod
    def get_cred_model_type() -> Type[ApiKeyCredsModel]:
        return ApiKeyCredsModel