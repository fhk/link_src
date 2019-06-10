import os

from werkzeug.debug.tbtools import get_current_traceback

from flask import request, render_template, jsonify

from link import app
from link.solve.main import (
    run_pcst,
    run_pamp,
    run_nfmp,
    run_spamp
    )

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/v1/pcst/submit', methods=['POST'])
def pcst():
    try:
        content = request.get_json()
        return jsonify(run_pcst(content))
    except Exception as e:
        track = get_current_traceback(skip=1, show_hidden_frames=True,
                    ignore_system_exceptions=False)
        track.log()
        abort(500)


if os.environ.get("TBART", False):
    from link.solve.main import run_pmed

    @app.route('/v1/pmed/submit', methods=['POST'])
    def pmed():
        try:
            content = request.get_json()
            return jsonify(run_pmed(content))
        except Exception as e:
            track = get_current_traceback(skip=1, show_hidden_frames=True,
                    ignore_system_exceptions=False)
            track.log()
            abort(500)


@app.route('/v1/pamp/submit', methods=['POST'])
def pamp():
    try:
        content = request.get_json()
        return jsonify(run_pamp(content))
    except Exception as e:
        track = get_current_traceback(skip=1, show_hidden_frames=True,
                    ignore_system_exceptions=False)
        track.log()
        abort(500)


@app.route('/v1/spamp/submit', methods=['POST'])
def spamp():
    try:
        content = request.get_json()
        return jsonify(run_spamp(content))
    except Exception as e:
        track = get_current_traceback(skip=1, show_hidden_frames=True,
                    ignore_system_exceptions=False)
        track.log()
        abort(500)


@app.route('/v1/nfmp/submit', methods=['POST'])
def nfmp():
    try:
        content = request.get_json()
        return jsonify(run_nfmp(content))
    except Exception as e:
        track = get_current_traceback(skip=1, show_hidden_frames=True,
                    ignore_system_exceptions=False)
        track.log()
        abort(500)


@app.route('/v1/get/<job>', methods=['GET'])
def get(job):
    return 0

