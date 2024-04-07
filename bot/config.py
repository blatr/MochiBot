import dotenv
from pathlib import Path
import os

config_dir = "config"
current_env = os.environ["APP_ENV"]

if current_env == "dev":
    env_path = Path(config_dir) / "dev.env"
elif current_env == "prod":
    env_path = Path(config_dir) / "prod.env"

config = dotenv.dotenv_values(env_path)

bot_token = config["BOT_TOKEN"]