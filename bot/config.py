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
enable_message_streaming = os.getenv("ENABLE_MESSAGE_STREAMING", config_yaml.get("enable_message_streaming", True))
return_n_generated_images = os.getenv("RETURN_N_GENERATED_IMAGES", config_yaml.get("return_n_generated_images", 1))
n_chat_modes_per_page = os.getenv("N_CHAT_MODES_PER_PAGE", config_yaml.get("n_chat_modes_per_page", 5))
mongodb_uri = os.getenv('MONGODB_URI', config_yaml.get("mongodb_uri"))
port = int(os.getenv('PORT', config_yaml.get("port", "8080")))

# chat_modes
with open(config_dir / "chat_modes.yml", 'r') as f:
    chat_modes = yaml.safe_load(f)

# prices
chatgpt_price_per_1000_tokens = float(os.getenv('CHATGPT_PRICE_PER_1000_TOKENS', config_yaml.get("chatgpt_price_per_1000_tokens", 0.002)))
gpt_price_per_1000_tokens = float(os.getenv('GPT_PRICE_PER_1000_TOKENS', config_yaml.get("gpt_price_per_1000_tokens", 0.02)))
whisper_price_per_1_min = float(os.getenv('WHISPER_PRICE_PER_1_MIN', config_yaml.get("whisper_price_per_1_min", 0.006)))
# models
with open(config_dir / "models.yml", 'r') as f:
    models = yaml.safe_load(f)

# files
help_group_chat_video_path = Path(__file__).parent.parent.resolve() / "static" / "help_group_chat.mp4"
