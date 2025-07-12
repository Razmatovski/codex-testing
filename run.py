from admin_app import create_app, ensure_db_initialized

app = create_app()
ensure_db_initialized(app)

if __name__ == '__main__':
    app.run(debug=True)

