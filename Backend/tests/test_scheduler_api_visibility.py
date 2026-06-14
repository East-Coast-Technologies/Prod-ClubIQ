from app import create_app
from config import TestingConfig


class SchedulerApiEnabledTestingConfig(TestingConfig):
    SCHEDULER_API_ENABLED = True


class SchedulerApiDisabledTestingConfig(TestingConfig):
    SCHEDULER_API_ENABLED = False


def _routes(config_class):
    app = create_app(config_class)
    return {str(rule) for rule in app.url_map.iter_rules()}


def test_scheduler_api_is_disabled_by_default_in_tests():
    routes = _routes(SchedulerApiDisabledTestingConfig)

    assert "/scheduler" not in routes
    assert "/scheduler/jobs" not in routes
    assert "/scheduler/jobs/<job_id>" not in routes


def test_scheduler_api_can_be_enabled_explicitly():
    routes = _routes(SchedulerApiEnabledTestingConfig)

    assert "/scheduler" in routes
    assert "/scheduler/jobs" in routes
