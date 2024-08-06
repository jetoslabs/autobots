from typing import Type

from src.autobots.secret.app_creds.app_creds_model import ApiKeyCredsModel
from src.autobots.secret.app_creds.app_creds_type.app_creds_type import AppCredsTypeABC
from src.autobots.secret.app_types import AppTypes


class JiraCreds(AppCredsTypeABC):

    @staticmethod
    def get_app() -> AppTypes:
        return AppTypes.jira

    @staticmethod
    def get_cred_model_type() -> Type[ApiKeyCredsModel]:
        return ApiKeyCredsModel