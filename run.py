from admin_app import create_app, ensure_db_initialized

app = create_app()

if __name__ == '__main__':
    ensure_db_initialized(app)
    app.run(debug=True)
