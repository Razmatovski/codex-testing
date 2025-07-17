import os
from admin_app import create_app, ensure_db_initialized

app = create_app()

if __name__ == '__main__':
    ensure_db_initialized(app)
    debug_env = os.environ.get('FLASK_DEBUG')
    if debug_env is not None:
        debug = debug_env.lower() == 'true'
    else:
        debug = app.config.get('DEBUG', False)
    app.run(debug=debug)
