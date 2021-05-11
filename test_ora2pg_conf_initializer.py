import os
import unittest

import ora2pg_conf_initializer as i

ORA2PG_CONFIG_FILE_PATH = "sample-data/ora2pg.conf"
ORA2PG_REFERENCE_CONFIG_FILE_PATH = "sample-data/ora2pg.conf.dist"
TEST_ORA2PG_CONFIG_FILE_PATH = ORA2PG_CONFIG_FILE_PATH + ".test"
TEST_ORA2PG_REFERENCE_CONFIG_FILE_PATH = ORA2PG_REFERENCE_CONFIG_FILE_PATH + ".test"


class InitializerTest(unittest.TestCase):
    @staticmethod
    def remove_file(path):
        try:
            os.remove(path)
            print(f"{path} removed")
        except OSError:
            pass

    @staticmethod
    def copy_file(src, destination):
        with open(src, "r") as src_file, open(destination, "w") as destination_file:
            part = src_file.read(4096)
            while part:
                destination_file.write(part)
                part = src_file.read(4096)

            print(f"File {src} copied to {destination}")

    def setUp(self):
        self.remove_file(TEST_ORA2PG_CONFIG_FILE_PATH)
        self.remove_file(TEST_ORA2PG_REFERENCE_CONFIG_FILE_PATH)
        self.copy_file(ORA2PG_REFERENCE_CONFIG_FILE_PATH,
                       TEST_ORA2PG_REFERENCE_CONFIG_FILE_PATH)

    def doCleanups(self):
        self.remove_file(TEST_ORA2PG_CONFIG_FILE_PATH)
        self.remove_file(TEST_ORA2PG_REFERENCE_CONFIG_FILE_PATH)

    def test_scenario_with_non_existing_config(self):
        os.environ["PG_SCHEMA"] = "CLAR"
        exit_code = i.main(TEST_ORA2PG_CONFIG_FILE_PATH, TEST_ORA2PG_REFERENCE_CONFIG_FILE_PATH)
        self.assertEqual(exit_code, i.EXIT_CODE_OK)
        self.assertTrue(os.path.exists(TEST_ORA2PG_CONFIG_FILE_PATH))
        with open(TEST_ORA2PG_CONFIG_FILE_PATH, "r") as file:
            lines = file.readlines()
            self.assertEqual(len(lines), 113)
            self.assertTrue("PG_SCHEMA CLAR\n" in lines)

    def test_scenario_with_existing_config(self):
        self.copy_file(ORA2PG_REFERENCE_CONFIG_FILE_PATH, TEST_ORA2PG_CONFIG_FILE_PATH)
        exit_code = i.main(TEST_ORA2PG_CONFIG_FILE_PATH, TEST_ORA2PG_REFERENCE_CONFIG_FILE_PATH)
        self.assertEqual(exit_code, i.EXIT_CODE_OK)

        with open(TEST_ORA2PG_CONFIG_FILE_PATH, "r") as file:
            lines = file.readlines()
            self.assertEqual(len(lines), 1251)
            self.assertTrue(
                "# with format; DDHH24MMSS::bigint, this depend of your apps usage.\n" in lines)

    def test_scenario_with_non_existing_reference_config(self):
        self.remove_file(TEST_ORA2PG_REFERENCE_CONFIG_FILE_PATH)
        exit_code = i.main(TEST_ORA2PG_CONFIG_FILE_PATH, TEST_ORA2PG_REFERENCE_CONFIG_FILE_PATH)
        self.assertEqual(exit_code, i.EXIT_CODE_ERROR)


if __name__ == '__main__':
    unittest.main()
