from flask import Flask, render_template, request, redirect, Response, url_for, send_file
import os, mimetypes, posixpath, json
import fs

ROOT_PATH = os.path.abspath("/Users/hechao/")
fs = fs.FsUtil(ROOT_PATH)

app = Flask(__name__)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route("/")
def fsop():
    path = request.args.get("path", ROOT_PATH)
    r = fs.ls(path)
    return render_template("fs.html", children=r["children"], path=path, parent=path)

def do_cat(path):
    return Response(json.dumps(fs.cat(path)))

def do_ls(path):
    return Response(json.dumps(fs.ls(path)))

def do_save(path):
    return Response(json.dumps("OK"))

route = {
        "cat": do_cat,
        "ls": do_ls,
        "save": do_save
        }

@app.route("/api")
def api():
    path = request.args.get("path", os.curdir)
    action = request.args.get("action", "")
    if not action:
        action = "ls" if os.path.isdir(path) else "cat"
    resp = route[action](path)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['content-type'] = 'application/json'
    return resp
    
if __name__ == '__main__':
  app.run(
      host="0.0.0.0",
      port=int("9011"),
      debug=False)
