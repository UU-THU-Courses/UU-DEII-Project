"""Module to parse the configurations provided by user."""

import yaml

def parse_configs(config_path) -> dict:
    """Load and return user configurations."""
    with open(config_path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            return config
        except yaml.YAMLError as exc:
            print(exc)

def write_configs(config_path, configs):
    """Write user configs to a path."""
    with open(config_path, "w") as stream:
        yaml.dump(configs, stream, default_flow_style=False)

if __name__ == "__main__":
    config = parse_configs("configs/cloud-cfg.yaml")
    write_configs("__temp/out_configs.yaml", config)
    config = parse_configs("configs/deploy-cfg.yaml")
    print(config)