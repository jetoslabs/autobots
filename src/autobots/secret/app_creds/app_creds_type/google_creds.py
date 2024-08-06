from typing import Type

from src.autobots.secret.app_creds.app_creds_model import OAuthCredsModel
from src.autobots.secret.app_creds.app_creds_type.app_creds_type import AppCredsTypeABC
from src.autobots.secret.app_types import AppTypes


class GoogleCreds(AppCredsTypeABC):

    @staticmethod
    def get_app() -> AppTypes:
        return AppTypes.google

    @staticmethod
    def get_cred_model_type() -> Type[OAuthCredsModel]:
        return OAuthCredsModel