from gevent import monkey
from flask import Flask, render_template
from flask import request
from parse import parse_mission
from gevent.pywsgi import WSGIServer
from flask_compress import Compress

monkey.patch_all()

app = Flask(__name__)

compress = Compress()
compress.init_app(app)
# Add support for static files
app.static_folder = "static"
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
        # response = jsonify(sqm_data)
        # return response, 200
        return render_template("file_upload.html", response=sqm_data)
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
    # app.run(debug=True, host="0.0.0.0", port=8080)
    http_server = WSGIServer(("0.0.0.0", 8080), app)
    http_server.serve_forever()
