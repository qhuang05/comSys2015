# -*- coding: utf-8 -*-
# !/usr/bin/python


import os

from flask import Flask, g, json
from flask_login import LoginManager

import pymysql


from src.biz import db
from src.web.system import view as system
from src import LoggedUser

PROJECT_PATH = os.path.dirname(__file__)

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    config_file = os.path.abspath(os.path.join(PROJECT_PATH, 'etc/config.py'))
    app.config.from_pyfile(config_file)

    config_log(app)
    config_db(app)
    config_route(app)


    app.logger.warn("app准备好了")

    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(userid):
        return LoggedUser(int(userid))

    return app


def config_log(app):
    import logging
    from logging.handlers import RotatingFileHandler

    format = '[%(asctime)s %(levelname)s]: %(message)s [in %(pathname)s:%(lineno)d]'
    log_file = app.config.get("LOG_FILE")
    if log_file:
        handler = RotatingFileHandler(
            log_file,
            maxBytes=10000,
            backupCount=10,
        )
        handler.setFormatter(logging.Formatter(format))
        app.logger.addHandler(handler)

    debug = app.debug
    if not debug:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(format))
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.WARN)

    app.logger.warn("xxxx")

def config_db(app):
    """
    配置数据
    :param app:
    :return:
    """
    db.configure_db(app)

    @app.before_request
    def before_request():
        g.db = pymysql.connect(host=app.config.get("MYSQL_HOST"), user=app.config.get("MYSQL_USER"),
                               passwd=app.config.get("MYSQL_PASS"), db=app.config.get("MYSQL_DB"),
                               port=int(app.config.get("MYSQL_PORT")))

    @app.teardown_request
    def teardown_request(exception):
        if hasattr(g, 'db'):
            g.db.close()


def config_route(app):
    """
    配置 url
    :param app:
    :return:
    """
    common_prefix = '/4test' if app.debug and app.config["WEIXIN_DEBUG"] else ''
    app.register_blueprint(system.bp, url_prefix=common_prefix)

    @app.errorhandler(400)
    def handler_400(error):
        return json.dumps(dict(message='参数不能为空:' + str(error.args))), 400




