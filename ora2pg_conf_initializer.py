""" This script creates /etc/ora2pg.conf file based on environment variables """

import os
import sys
import time
from os.path import exists

EXIT_CODE_OK, EXIT_CODE_ERROR = 0, 1


def current_time_millis():
    """ Get current time in milliseconds """
    return round(time.time() * 1000)


class Ora2PgSetting:
    """ Class that represents an ora2pg configuration setting """

    def __init__(self, name, default_value, optional):
        self.name = name
        self.default_value = default_value
        self.optional = optional
        self.env_value = os.getenv(name)

    def __str__(self):
        return f"{self.name} {self.get_value()}"

    def is_required_or_env_value_supplied(self):
        """ Is this setting required? It is required when it is not commented in reference config
        file or environment variable supplies the value for it """
        return not self.optional or (self.optional and self.env_value is not None)

    def get_value(self):
        """ Get the actual value of the setting. Returns default value or value provided by
         environment variable if there is one """
        return self.env_value if self.env_value is not None else self.default_value


def filter_lines_with_settings(lines):
    """ filters the lines and returns only strings that contain required or optional setting """

    def is_setting(line):
        skipped_prefixes = ["# ", "#-", "##", "#WHERE", "#in"]
        return len(line) > 2 and not [p for p in skipped_prefixes if line.startswith(p)]

    def clear_line(line):
        return ' '.join(line.strip().split())

    def remove_comments(line):
        result = remove_comments(line[:line.rfind("#")]) if line.count("#") > 1 else line
        return result.strip()

    return [remove_comments(line) for line in map(clear_line, lines) if is_setting(line)]


def read_reference_settings(path):
    """ read settings from reference config file and return the list of Ora2PgSetting objects """

    def line_to_setting(line):
        optional = line.startswith("#")
        line = line.replace("#", "")
        name = line.strip() if line.find(" ") == -1 else line[:line.find(" ")]
        value = "" if line.find(" ") == -1 else line[line.find(" ") + 1:]
        return Ora2PgSetting(name, value, optional)

    with open(path, "r") as file:
        return list(map(line_to_setting, filter_lines_with_settings(file.readlines())))


def write_config_file(path, settings):
    """ Write setting to destination file specified by path parameter """
    print(f"Writing configuration to {path}")

    with open(path, "w") as file:
        for setting in settings:
            # print(setting)
            file.write(f"{setting.name} {setting.get_value()}\n")


def initialize_ora2pg_conf(conf_location, dist_conf_location):
    """ Create config file or do nothing if it already exists """
    print(f"Initializing the ora2pg configuration. Path: {conf_location}")

    if exists(conf_location):
        print(f"{conf_location} already exists, so nothing to do here, because someone already"
              f" created the file")

        return EXIT_CODE_OK

    if not exists(dist_conf_location):
        print(f"Error. Cannot find the reference configuration file {dist_conf_location}")
        return EXIT_CODE_ERROR

    print(f"Reference configuration file found. Path: {dist_conf_location}")

    settings = read_reference_settings(dist_conf_location)

    print("Reference configuration file was successfully read")

    write_config_file(conf_location,
                      list(filter(lambda s: s.is_required_or_env_value_supplied(), settings)))

    return EXIT_CODE_OK


def main(conf_location, dist_conf_location):
    """ Main function """

    try:
        started_at = current_time_millis()
        exit_code = initialize_ora2pg_conf(conf_location, dist_conf_location)
    except OSError:
        exit_code = EXIT_CODE_ERROR
    finally:
        print("Elapsed {}ms".format(current_time_millis() - started_at))

    return exit_code


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Locations of ora2pg.conf and ora2pg.conf.dist files should be specified as "
              "command-line arguments")
        sys.exit(EXIT_CODE_ERROR)
    sys.exit(main(sys.argv[1], sys.argv[2]))
