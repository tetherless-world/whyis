basestring = getattr(__builtins__, 'basestring', str)


def config_str_to_obj(cfg):
    if isinstance(cfg, basestring):
        module = __import__('config', fromlist=[cfg])
        return getattr(module, cfg)
    return cfg


def app_factory(config, app_name, blueprints=None):
    from main import App, PROJECT_PATH
    # you can use Empty directly if you wish
    app = App(app_name, root_path=PROJECT_PATH)
    config = config_str_to_obj(config)
    #print dir(config)
    app.configure(config)
    if blueprints:
        app.add_blueprint_list(blueprints)
    app.setup()

    return app
