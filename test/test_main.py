import os

from link.solve.main import (
    run_pcst,
    run_pmed,
    run_pamp,
    run_nfmp
 )

SIMPLE_INPUT = {"type": "FeatureCollection", "features": [
    {"type": "Feature",
    "geometry": {
        "type": "LineString",
        "coordinates": [
            [18.38724584292816, -34.10317093131459],
            [18.38742811501918, -34.10332185781299]]
    },
    "properties":
        {"node_1": str([18.38987647256616, -34.104647551974494]), 
        "node_2": str([18.3901436622786, -34.104491994918384]),
        "length": 25.775978637305705}
    },
    {"type": "Feature",
        "geometry":{
            "type": "LineString",
            "coordinates": [
                [18.387538414105652, -34.10308825999736],
                [18.38724584292816, -34.10317093131459]]
            },
    "properties": 
        {"node_1": str([18.38987647256616, -34.104647551974494]),
        "node_2": str([18.3901436622786, -34.104491994918384]),
        "length": 33.681673041196234}
    },
    {"type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates":
            [18.387538414105652, -34.10308825999736],
        },
    "properties": 
        {"demand": 1}
    },
    {"type": "Feature",
    "geometry":{
        "type": "Point",
        "coordinates":
            [18.38742811501918, -34.10332185781299],
    },
    "properties":
         {"capacity": 500,
          "candidate": 500}
}]}

if os.environ.get("TBART", False):
    def test_pmed():
        assert run_pmed(SIMPLE_INPUT)


def test_pcst():
    assert run_pcst(SIMPLE_INPUT)


def test_pamp():
    assert run_pamp(SIMPLE_INPUT)


def test_nfmp():
    assert run_nfmp(SIMPLE_INPUT)

