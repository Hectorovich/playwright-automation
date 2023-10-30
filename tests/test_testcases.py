from pytest import mark

data = [
    ("hello", "world"),
    ("hello", ""),
    ("123", "world"),
]

ddt = {
    "argnames": "name,description",
    "argvalues": data,
    "ids": ["general test", "test with no description", "test with digit name"]
}


@mark.parametrize(**ddt)
def test_new_testcase(desktop_app_auth, name, description):
    desktop_app_auth.navigate_to("Create new test")
    desktop_app_auth.create_test(name, description)
    desktop_app_auth.navigate_to("Test Cases")
    check_presence = desktop_app_auth.test_cases.check_test_exists(name)
    desktop_app_auth.test_cases.delete_test_by_name(name)

    assert check_presence


def test_testcase_does_not_exist(desktop_app_auth):
    desktop_app_auth.navigate_to("Test Cases")
    assert not desktop_app_auth.test_cases.check_test_exists("fdg")
