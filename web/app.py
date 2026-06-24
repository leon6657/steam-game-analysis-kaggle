"""
Flask 应用入口
"""

import os
import sys

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from flask import Flask
from web.routes import bp, init_app


def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.template_folder = os.path.join(_project_root, "web", "templates")
    app.static_folder = os.path.join(_project_root, "web", "static")
    with app.app_context():
        init_app()
    return app


if __name__ == "__main__":
    app = create_app()
    print(f"[app] 启动于 http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
