"""Module to parse the configurations provided by user."""

import yaml

def parse_configs(config_path) -> dict:
    """Load and return user configurations."""
    with open(config_path, "r") as fstream:
        try:
            config = yaml.safe_load(fstream)
            return config
        except yaml.YAMLError as exc:
            print(exc)

def write_configs(config_path, configs):
    """Write user configs to a path."""
    with open(config_path, "w") as fstream:
        yaml.safe_dump(configs, fstream, default_flow_style=False, width=8096)

if __name__ == "__main__":
    config = parse_configs("configs/headnode-cfg.yaml")
    print(config["users"])
    write_configs("__temp__/out_configs.yaml", config)
    print("\n\n\n")
    config = parse_configs("configs/deploy-cfg.yaml")
    print(config)