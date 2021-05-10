import os
import sys
import time
from os.path import exists


def current_time_millis():
    return round(time.time() * 1000)


class Ora2PgSetting:
    def __init__(self, name, default_value, optional):
        self.name = name
        self.default_value = default_value
        self.optional = optional
        self.env_value = os.getenv(name)

    def __str__(self):
        return f"{self.name} {self.get_value()}"

    def is_required_or_env_value_supplied(self):
        return not self.optional or (self.optional and self.env_value is not None)

    def get_value(self):
        return self.env_value if self.env_value is not None else self.default_value


def filter_lines_with_settings(lines):
    def is_setting(config_line):
        return len(config_line) > 2 and not [prefix for prefix in ["# ", "#-", "##", "#WHERE", "#in"] if config_line.startswith(prefix)]

    def clear_line(config_line):
        return ' '.join(config_line.strip().split())

    def remove_comments(config_line):
        return remove_comments(config_line[:config_line.rfind("#")]).strip() if config_line.count("#") > 1 else config_line.strip()

    return [remove_comments(line) for line in map(clear_line, lines) if is_setting(line)]


def read_reference_settings(path):
    def line_to_setting(line):
        optional = line.startswith("#")
        line = line.replace("#", "")
        name = line.strip() if line.find(" ") == -1 else line[:line.find(" ")]
        value = "" if line.find(" ") == -1 else line[line.find(" ") + 1:]
        return Ora2PgSetting(name, value, optional)

    with open(path, "r") as file:
        return list(map(line_to_setting, filter_lines_with_settings(file.readlines())))


def write_config_file(path, settings):
    print(f"Writing configuration to {path}")

    with open(path, "w") as file:
        for setting in settings:
            print(setting)
            file.write(f"{setting.name} {setting.get_value()}\n")


def initialize_ora2pg_conf(conf_location="/etc/ora2pg.conf", dist_conf_location="/etc-ora2pg/ora2pg.conf.dist"):
    print(f"Initializing the ora2pg configuration. Path: {conf_location}")

    if exists(conf_location):
        print(f"{conf_location} already exists, so nothing to do here, because someone already created the file")
        return 0

    if not exists(dist_conf_location):
        print(f"Error. Cannot find the reference configuration file {dist_conf_location}")
        return 1

    print(f"Reference configuration file found. Path: {dist_conf_location}")

    settings = read_reference_settings(dist_conf_location)

    print("Reference configuration file was successfully read")

    write_config_file(conf_location, list(filter(lambda s: s.is_required_or_env_value_supplied(), settings)))

    return 0


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Locations of ora2pg.conf and ora2pg.conf.dist files should be specified as command-line arguments")
        exit(1)

    try:
        started_at = current_time_millis()
        exit_code = initialize_ora2pg_conf(conf_location=sys.argv[1], dist_conf_location=sys.argv[2])
    except:
        exit_code = 1
    finally:
        print("Elapsed {}ms".format(current_time_millis() - started_at))
        exit(exit_code)
