from autobots.core.settings import SettingsProvider


def set_test_settings():
    print("Settings for tests")
    SettingsProvider.set_env_file(".env.test")


set_test_settings()
