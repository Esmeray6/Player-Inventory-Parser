import os
import sys
from gevent import monkey
from flask import Flask, render_template
from flask import request
from parse import parse_mission
from gevent.pywsgi import WSGIServer
from flask_compress import Compress

host = "127.0.0.1"
port = 8080

if getattr(sys, "frozen", False):
    template_folder = os.path.join(sys._MEIPASS, "templates")
    static_folder = os.path.join(sys._MEIPASS, "static")
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)
current_path = os.path.dirname(os.path.abspath(__file__))
print(current_path)

monkey.patch_all()

compress = Compress()
compress.init_app(app)
# Add support for static files

template_folder = app.template_folder
print(f"Template folder: {template_folder}")
# app.config["APPLICATION_ROOT"] = "/"
# app.config["SERVER_NAME"] = "localhost:5000"

# with open("data_unorganized.json") as file:
#     item_data = json.load(file)


@app.route("/")
def hello_world():
    return render_template("index.html")


# Accept a file upload and receive it as a string
@app.route("/fileUpload", methods=["POST"])
def file_upload():
    if request.method == "POST":
        file = request.files.get("fileToUpload")
        if file is None:
            return render_template("no_file.html"), 400
        # sqm_data = file.stream.read().decode("utf-8")
        sqm_data = parse_mission(file.stream.read().decode("utf-8"))
        # pprint(sqm_data)
        # response = jsonify(sqm_data)
        # return response, 200
        return render_template("file_upload.html", mission_name=sqm_data[0], response=sqm_data[1])
    return "Incorrect", 400


@app.errorhandler(404)
def page_not_found(error: Exception):
    return (
        render_template(
            "error.html",
            error_string="Not Found",
        ),
        404,
    )


@app.errorhandler(500)
def internal_server_error(error: Exception):
    return (
        render_template(
            "error.html",
            error_string="Internal Server Error. Perhaps wrong file format?",
        ),
        500,
    )


if __name__ == "__main__":
    # app.run(debug=True, host=host, port=port)
    print(f"Running on: http://{host}:{port}")
    http_server = WSGIServer((host, port), app)
    http_server.serve_forever()
