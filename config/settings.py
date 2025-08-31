from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv
from typing import List
import ast

load_dotenv()


class Settings(BaseSettings):
    # Bot settings
    bot_token: str = Field(..., env="BOT_TOKEN")

    # Channel settings
    channel_id: str = Field(..., env="CHANNEL_ID")  # Format: @channelname or -100123456789
    channel_invite_link: str = Field(..., env="CHANNEL_INVITE_LINK")

    # Supabase settings
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_service_role_key: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")

    # SQLite settings
    sqlite_db_path: str = Field(default="bot_database.db", env="SQLITE_DB_PATH")

    # Referral settings
    referral_points: int = Field(default=10, env="REFERRAL_POINTS")

    # Admin settings
    admin_ids: List[int] = Field(default_factory=list)

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse admin IDs from environment variable
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if admin_ids_str:
            try:
                # Handle both list format [1,2,3] and comma-separated format 1,2,3
                if admin_ids_str.startswith('[') and admin_ids_str.endswith(']'):
                    # Parse as Python list literal
                    self.admin_ids = ast.literal_eval(admin_ids_str)
                else:
                    # Parse as comma-separated string
                    self.admin_ids = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing ADMIN_IDS: {e}")
                self.admin_ids = []


settings = Settings()