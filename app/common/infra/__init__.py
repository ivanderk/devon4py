import logging
from enum import Enum

from fastapi import FastAPI
from pydantic import ValidationError

from app.common.core.configuration import load_env_file_on_settings
from app.common.infra.firebase import FirebaseSettings, get_firebase_settings, FirebaseService, configure_firebase_api
from app.common.core.identity_provider import IdentityProvider
from app.common.infra.keycloak import KeycloakSettings, get_keycloak_settings, KeycloakService, configure_keycloak_api


logger = logging.getLogger(__name__)


class IDPType(Enum):
    KEYCLOAK = KeycloakService, KeycloakSettings
    FIREBASE = FirebaseService, FirebaseSettings


def __get_idp() -> (IdentityProvider, IDPType):
    """Factory that creates the instance of the Identity Provider given the app configuration"""
    for idp_enum_value in IDPType:
        try:
            service_type, settings_type = idp_enum_value.value
            settings = load_env_file_on_settings(settings_type)  # Throws ValidationError
        except ValidationError:
            pass
        else:
            logger.info(f"Initializing IDP of type {service_type}")
            return service_type(settings), idp_enum_value
    return None, None


# TODO: Add this as class method (and refactor this file)
def configure_api(api: FastAPI):
    if idp_type == IDPType.KEYCLOAK:
        configure_keycloak_api(api)
    if idp_type == IDPType.FIREBASE:
        configure_firebase_api(api)


idp_configuration = __get_idp()

idp: IdentityProvider = idp_configuration[0]
idp_type: IDPType = idp_configuration[1]
