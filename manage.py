from flask.ext.script import Manager, prompt_bool, Shell, Server
from termcolor import colored
import logging
from link import app


manager = Manager(app)


def make_shell_context():
    return dict(app=app)

manager.add_command('runserver', Server(host="0.0.0.0", port=8080))
manager.add_command('shell', Shell(make_context=make_shell_context))
gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)
app.logger.debug('Start of new run.')


if __name__ == '__main__':
    manager.run()
