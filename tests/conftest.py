def pytest_addoption(parser):
    parser.addoption(
        "--no-prompts", action="store_true", default=False, help="Skip the tests which prompt the user for confirmation"
    )
