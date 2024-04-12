import os
import shutil
import subprocess
import sys
from gevent import monkey
from flask import Flask, render_template
from flask import request
from parse import parse_mission
from gevent.pywsgi import WSGIServer
from flask_compress import Compress

# 0 for DEBUG, 1 for PRODUCTION
MODE = 0
host = "127.0.0.1"
port = 8080

if getattr(sys, "frozen", False):
    template_folder = os.path.join(sys._MEIPASS, "templates")  # type: ignore
    static_folder = os.path.join(sys._MEIPASS, "static")  # type: ignore
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)
current_path = os.path.dirname(os.path.abspath(__file__))
print(current_path)

if MODE == 1:
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
        source_file = request.files.get("missionFile")
        if source_file is None:
            return render_template("error.html", error_string="Mission file not found"), 400
        # sqm_data = file.stream.read().decode("utf-8")
        # Save the file to the current working directory
        internal_dir = os.path.join(os.getcwd(), "_internal")
        if not os.path.isdir(internal_dir):
            os.mkdir(internal_dir)

        destination_dir = os.path.join(internal_dir, "mission.sqm")
        source_file.save(destination_dir)
        source_file.close()
        equipment_file = request.files.get("equipmentFile")
        if equipment_file is None:
            return (
                render_template("error.html", error_string="Equipment file not found"),
                400,
            )
        equipment_path = os.path.join(internal_dir, "AET_equipment.sqf")
        equipment_file.save(equipment_path)
        equipment_file.close()

        # os.makedirs(destination_dir, exist_ok=True)

        # Define the path to the batch file inside the "_internal" folder
        batch_file_path = os.path.join(internal_dir, "MissionDerap.bat")

        # Run the batch file using subprocess
        subprocess.run([batch_file_path, destination_dir], shell=True)

        sqm_data = parse_mission(destination_dir, equipment_path)
        # pprint(sqm_data)
        # response = jsonify(sqm_data)
        # return response, 200
        return render_template(
            "file_upload.html", mission_name=sqm_data[0], response=sqm_data[1]
        )
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
    if MODE == 0:
        app.run(debug=True, host=host, port=port)
    elif MODE == 1:
        print(f"Running on: http://{host}:{port}")
        http_server = WSGIServer((host, port), app)
        http_server.serve_forever()
