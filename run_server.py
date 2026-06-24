from web.app import create_app
app = create_app()
print("Server starting at http://127.0.0.1:5000")
app.run(host="127.0.0.1", port=5000, debug=False)
