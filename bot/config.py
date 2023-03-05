import os
import yaml
import dotenv
from pathlib import Path

config_dir = Path(__file__).parent.parent.resolve() / "config"

# load yaml config
try:
    with open(config_dir / "config.yml", 'r') as f:
        config_yaml = yaml.safe_load(f)
except:
    config_yaml = {}
# load .env config
config_env = dotenv.dotenv_values(config_dir / "config.env")

# config parameters
telegram_token = os.getenv('TELEGRAM_TOKEN', config_yaml.get("telegram_token"))
openai_api_key = os.getenv('OPENAI_API_KEY', config_yaml.get("openai_api_key"))
use_chatgpt_api = os.getenv('USE_CHATGPT_API', config_yaml.get("use_chatgpt_api", True))
allowed_telegram_usernames = config_yaml.get('allowed_telegram_usernames', list(filter(None, os.getenv("TELEGRAM_USERNAMES", "").split(','))))
new_dialog_timeout = int(os.getenv("NEW_DIALOG_TIMEOUT", config_yaml.get("new_dialog_timeout")))
mongodb_uri = os.getenv('MONGODB_URI', config_yaml.get("mongodb_uri"))
port = int(os.getenv('PORT', config_yaml.get("port", "8080")))
webhook_url = os.getenv('TELEGRAM_WEBHOOK_URL', config_yaml.get("webhook_url"))