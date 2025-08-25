import yaml
import os

class ConfigManager:
    _instance = None

    def __new__(cls, config_path='config/config.yaml'):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config(config_path)
        return cls._instance

    def _load_config(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self._override_with_env_vars(self.config)

    def _override_with_env_vars(self, config_dict, prefix=''):
        for key, value in config_dict.items():
            full_key = f"{prefix}{key}".upper()
            if isinstance(value, dict):
                self._override_with_env_vars(value, f"{full_key}_")
            else:
                env_value = os.getenv(full_key)
                if env_value is not None:
                    # Attempt to convert to original type
                    if isinstance(value, int):
                        config_dict[key] = int(env_value)
                    elif isinstance(value, float):
                        config_dict[key] = float(env_value)
                    elif isinstance(value, bool):
                        config_dict[key] = env_value.lower() in ('true', '1', 't')
                    else:
                        config_dict[key] = env_value

    def get(self, key, default=None):
        keys = key.split('.')
        val = self.config
        try:
            for k in keys:
                val = val[k]
            return val
        except KeyError:
            return default

    def set(self, key, value):
        keys = key.split('.')
        val = self.config
        for i, k in enumerate(keys):
            if i == len(keys) - 1:
                val[k] = value
            else:
                if k not in val or not isinstance(val[k], dict):
                    val[k] = {}
                val = val[k]


config = ConfigManager()

