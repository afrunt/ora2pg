import os
import sys
import time
from os.path import exists


def current_time_millis(): return round(time.time() * 1000)


def only_lines_with_settings(lines):
    def is_setting(config_line):
        return len(config_line) > 2 and not [prefix for prefix in ["# ", "#-", "##", "#WHERE", "#in"] if config_line.startswith(prefix)]

    def remove_comments(config_line):
        return remove_comments(config_line[:config_line.rfind("#")]).strip() if config_line.count("#") > 1 else config_line.strip()

    def clear_lines(lines_to_clear):
        return [' '.join(line.strip().split()) for line in lines_to_clear]

    return [remove_comments(line) for line in clear_lines(lines) if is_setting(line)]


def lines_to_settings(lines):
    def line_to_setting(line):
        optional = line.startswith("#")
        line = line.replace("#", "")
        return (line.strip(), "", optional) if line.find(" ") == -1 else (line[:line.find(" ")], line[line.find(" ") + 1:], optional)

    return [line_to_setting(str(line)) for line in lines]


def populate_env_values(settings):
    def choose_value(value, env_value): return value if env_value is None else env_value

    def is_required_or_optional_value_supplied(optional, env_value):
        return not optional or (optional and env_value is not None)

    def with_env_values(settings_to_enrich):
        return [(key, value, optional, os.getenv(key)) for (key, value, optional) in settings_to_enrich]

    return [(key, choose_value(value, env_value)) for (key, value, optional, env_value) in
            with_env_values(settings) if is_required_or_optional_value_supplied(optional, env_value)]


def read_reference_settings(path):
    with open(path, "r") as file:
        return lines_to_settings(only_lines_with_settings(file.readlines()))


def write_config_file(path, settings):
    print(f"Writing configuration to {path}")

    with open(path, "w") as file:
        for (key, value) in settings:
            print(f"{key} {value}")
            file.write(f"{key} {value}\n")


def initialize_ora2pg_conf(conf_location="/etc/ora2pg.conf", dist_conf_location="/etc-ora2pg/ora2pg.conf.dist"):
    print(f"Initializing the ora2pg configuration. Path: {conf_location}")

    if exists(conf_location):
        print(f"{conf_location} already exists, so nothing to do here, because someone already created the file")
        return 0

    if not exists(dist_conf_location):
        print(f"Error. Cannot find the reference configuration file {dist_conf_location}")
        return 1

    print(f"Reference configuration file found. Path: {dist_conf_location}")

    settings = populate_env_values(read_reference_settings(dist_conf_location))

    print("Reference configuration file was successfully read")

    write_config_file(conf_location, settings)

    return 0


if __name__ == '__main__':
    started_at = current_time_millis()

    if len(sys.argv) != 3:
        print("Locations of ora2pg.conf and ora2pg.conf.dist files should be specified as command-line arguments")
        exit(1)

    exit_code = initialize_ora2pg_conf(conf_location=sys.argv[1], dist_conf_location=sys.argv[2])

    print("Elapsed {}ms".format(current_time_millis() - started_at))

    exit(exit_code)
