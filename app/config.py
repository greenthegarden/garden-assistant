from pydantic import BaseSettings

class AppConfig(BaseSettings):
    app_name: str = "Garden Assistant"
    admin_email: str = "greenthegarden@gmail.com"
    items_per_user: int = 50

    class Config:
        env_file = ".env"

config = AppConfig()
