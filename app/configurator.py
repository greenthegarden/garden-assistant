# Code based on https://medium.com/@wilde.consult/lovely-python-config-handling-using-pydantic-852d9be2320f

# BUILTIN modules
import os
import sys
import site
from typing import Union, Type, Tuple

# Third party modules
from pydantic import Field, field_validator
from pydantic_settings import (BaseSettings, SettingsConfigDict,
                               PydanticBaseSettingsSource)

# Constants
MISSING_ENV = '>>> undefined ENV parameter <<<'
""" Error message for missing environment variables. """
MISSING_SECRET = '>>> missing SECRETS file <<<'
""" Error message for missing secrets file. """
SECRETS_DIR = ('/run/secrets'
               if os.path.exists('/.dockerenv')
               else f'{site.USER_BASE}/secrets')
""" This is where your secrets are stored (in Docker or locally). """
PLATFORM = {'linux': 'Linux', 'linux2': 'Linux',
            'win32': 'Windows', 'darwin': 'MacOS'}
""" Known platforms in my end of the world. """
ENVIRONMENT = os.getenv('ENVIRONMENT', MISSING_ENV)
""" Define environment. """


# --------------------------------------------------------------
# This needs to be done before the Base class gets evaluated, and
# to avoid getting five UserWarnings that the path does not exist.
#
# Create the directory if it does not already exist. When running
# inside Docker, skip it (Docker handles that just fine on its own).
#
if not os.path.exists('/.dockerenv'):
    os.makedirs(SECRETS_DIR, exist_ok=True)

# ------------------------------------------------------------------------
#
class Common(BaseSettings):
    """ Common configuration parameters shared between all environments.

    Read configuration parameters defined in this class, and from
    ENVIRONMENT variables and from the .env file.

    The source priority is changed (from default) to the following
    order (from highest to lowest)::
      - init_settings
      - dotenv_settings
      - env_settings
      - file_secret_settings

    The following environment variables should already be defined::
      - HOSTNAME (on Linux servers only - set by OS)
      - COMPUTERNAME (on Windows servers only - set by OS)
      - ENVIRONMENT (on all servers - "dev" is default when missing)

    Path where your <environment>.env file should be placed::
      - linux: /home/<user>/.local
      - darwin: /home/<user>/.local
      - win32: C:\\Users\\<user>\\AppData\\Roaming\\Python'

    Path where your secret files should be placed::
      - linux: /home/<user>/.local/secrets
      - darwin: /home/<user>/.local/secrets
      - win32: C:\\Users\\<user>\\AppData\\Roaming\\Python\\secrets'

    You know you are running in Docker when the "/.dockerenv" file exists.
    """
    model_config = SettingsConfigDict(extra='ignore',
                                      secrets_dir = SECRETS_DIR,
                                      env_file_encoding = 'utf-8',
                                      env_file = ('.env', f'{site.USER_BASE}/.env')
    )
    print(model_config)

    # secrets...
    admin_email: str = MISSING_SECRET

    # Normal stuff.
    api_timeout: tuple = (9.05, 60)
    app_name: str = "Garden Assistant"
    env: str = os.getenv('ENVIRONMENT', 'dev')
    header_data: dict = {'Content-Type': 'application/json'}
    items_per_user: int = 50
    platform: str = PLATFORM.get(sys.platform, 'other')
    server: str = Field(MISSING_ENV, alias=('COMPUTERNAME'
                                            if sys.platform == 'win32'
                                            else 'HOSTNAME'))

    @field_validator('server')
    def remove_domain(cls, value) -> str:
        """ Return server name stripped of possible domain part. """
        return value.upper().split('.')[0]

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """ Change source priority order (env trumps environment). """
        return (init_settings, dotenv_settings,
                env_settings, file_secret_settings)



# ------------------------------------------------------------------------
#
class Dev(Common):
    """ Configuration parameters for DEV environment.

    Values from dev.env supersedes previous values when the file exists.
    """

    env: str = 'dev'

    model_config = SettingsConfigDict(env_file=('.env', f'{site.USER_BASE}f/{env}.env'))


# ------------------------------------------------------------------------
#
class Test(Common):
    """ Configuration parameters for TEST environment.

    Values from test.env supersedes previous values when the file exists.
    """

    env: str = 'test'

    model_config = SettingsConfigDict(env_file=('.env', f'{site.USER_BASE}f/{env}.env'))


# ------------------------------------------------------------------------
#
class Stage(Common):
    """ Configuration parameters for STAGE environment.

    Values from stage.env supersedes previous values when the file exists.
    """

    env: str = 'stage'

    model_config = SettingsConfigDict(env_file=('.env', f'{site.USER_BASE}f/{env}.env'))


# ------------------------------------------------------------------------
#
class Prod(Common):
    """ Configuration parameters for PROD environment.

    Values from prod.env supersedes previous values when the file exists.
    """

    env: str = 'prod'

    model_config = SettingsConfigDict(env_file=('.env', f'{site.USER_BASE}f/{env}.env'))
    
# ------------------------------------------------------------------------

# Translation table between ENVIRONMENT value and their classes.
_setup = dict(
    dev=Dev,
    test=Test,
    prod=Prod,
    stage=Stage
)

# Validate and instantiate specified environment configuration.
config: Union[Dev, Test, Prod, Stage] = _setup[ENVIRONMENT]()
