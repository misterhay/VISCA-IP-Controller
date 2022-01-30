import pytest

from visca_over_ip import Camera


@pytest.fixture
def cam():
    return Camera('172.16.0.203')


class ManualVerifyFailure(Exception):
    """Raised when the person running the test does not think that the driver code is working right"""
    pass


@pytest.fixture
def cli_verify(pytestconfig):
    def check_expectation(expectation: str):
        while True:
            response = input(f'Verify that {expectation} (Y/n): ')
            response = response.lower().strip()

            if response in ['y', '']:
                return
            elif response == 'n':
                raise ManualVerifyFailure(f'The tests expected "{expectation}" but that didn\'t happen')
            else:
                print('Enter "y" or "n"')

    if pytestconfig.getoption('--no-prompts'):
        return lambda expectation: None  # no-op
    else:
        return check_expectation
