from config_parser import parse_config

if __name__ == "__main__":
    config = parse_config("/config/energy-pipeline.json")
    print("Config loaded successfully:")
    print(config)