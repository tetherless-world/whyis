from whyis.app_factory import app_factory


def heroku():
    from config import Config, project_name
    # setup app through APP_CONFIG envvar
    return app_factory(Config, project_name)
