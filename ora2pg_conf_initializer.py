import os
import sys
from os.path import exists


def only_lines_with_settings(lines):
    filtered_lines = []

    def not_just_a_comment(config_line):
        result = True
        for prefix in ["# ", "#-", "##", "#WHERE", "#in"]:
            result = result and not str(config_line).startswith(prefix)

        return result

    def clean_up_line(config_line):
        config_line_str = str(config_line)
        if config_line_str.count("#") > 1:
            return clean_up_line(config_line_str[:config_line_str.rfind("#")]).strip()
        else:
            return config_line_str.strip()

    for line in lines:
        line_str = ' '.join(str(line).strip().split())
        if not len(line_str) < 2 and not_just_a_comment(line_str):
            filtered_lines.append(clean_up_line(line_str))

    return filtered_lines


def lines_to_settings(lines):
    settings = []
    for line in lines:
        optional = False
        line_str = str(line)
        if line_str.startswith("#"):
            optional = True
            line_str = line_str[1:]

        if line_str.find(" ") == -1:
            settings.append((line_str.strip(), "", optional))
        else:
            settings.append((line_str[:line_str.find(" ")], line_str[line_str.find(" ") + 1:], optional))

    return settings


def populate_env_values(settings):
    def choose_value(default, env_value):
        return default if env_value is None else env_value

    def required_or_optional_value_supplied(optional, env_value):
        return not optional or (optional and env_value is not None)

    settings_with_env_values = [(key, value, optional, os.getenv(key)) for (key, value, optional) in settings]

    return [(key, choose_value(value, env_value)) for (key, value, optional, env_value) in
            settings_with_env_values if required_or_optional_value_supplied(optional, env_value)]


def write_config_file(path, settings):
    print(f"Writing configuration to {path}")

    with open(path, "w") as file:
        for (key, value) in settings:
            print(f"{key} -> {value}")
            file.write(f"{key} {value}\n")

    pass


def initialize_ora2pg_conf(conf_location="/etc/ora2pg.conf", dist_conf_location="/etc-ora2pg/ora2pg.conf.dist"):
    print(f"Initializing the ora2pg configuration. Path: {conf_location}")

    if exists(conf_location):
        print(f"{conf_location} already exists, so nothing to do here, because someone already created the file")
        exit(0)

    if not exists(dist_conf_location):
        print(f"Error. Cannot find the reference configuration file {dist_conf_location}")
        exit(1)

    print(f"Reference configuration file found. Path: {dist_conf_location}")

    with open(dist_conf_location, "r") as file:
        ref_conf_lines = only_lines_with_settings(file.readlines())

    settings = populate_env_values(lines_to_settings(ref_conf_lines))

    print("Reference configuration file was successfully read")

    write_config_file(conf_location, settings)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Locations of ora2pg.conf and ora2pg.conf.dist files should be specified as command-line arguments")
        exit(1)

    initialize_ora2pg_conf(conf_location=sys.argv[1], dist_conf_location=sys.argv[2])
