# LINK - a solver to connect things

# What is LINK
There are many infrastructure and logistics design problems that can be modelled/approximated by the following topological concepts.

1. Tree
2. Star
3. Ring

Whilst it is possible to model most of these purely as Mixed Integer Programs (MIP's) this does not scale well. Therefore, by using some Huersitics and algos the functionality seeks to yield equivalent results in a much more rapid timeframe.

This can be used to solve such problems as infrastructure networks which consist of power, logistics, fixed and/or wireless communications connections.

# Functionality

- [X] Solve a tree, prize collecting steiner tree problem
- [X] Solve capacitated p-median problem Tietz Bart
- [X] Solve network flow/tree model with capacitated edges
- [X] Create API
- [ ] Store requests and solves in DB
- [X] Solve p-median with setup cost, similar to or-tools assignment MIP
- [ ] Parralelize p-median solve
- [ ] Make solutions retrievable
- [X] Add HTTPS
- [ ] Add tiers with in a solution
- [ ] Add graph paritioning
- [ ] Add trans-shipment formulation and data processing
- [ ] Add multiple solvers XPRESS, Gurobi ...
- [ ] Add CP implemenations and solvers
- [ ] Add or-tools models for TSP
- [ ] Comply with pep8
- [ ] Refactor graph-tool v. networkx handling
- [ ] Ideas ???

# Support
This functionality currently works on OS-X and Linux. Docker containers can also be built.

# How it works

The application is both a REST endpoint and a Python module.

The functionality to take the data from GeoJSON to internal graph to solution back to GeoJSON output is contained in the "solve" module.

Depending on which endpoint is being used the graph functionality is either transformed in to input or into a derived graph. A assignment graph creates a link from the possible candidate locations to the demand locations.

# Make it work
Link requires a GeoJSON input that can be turned into a fully connected graph. The submission should be a "FeatureCollection" containing "Point" and "LineString" objects with the following attributes:
### LineString
- ID
- length

### Point
- ID
- demand
- candidate int representing the max exploration distance from the point 
- capacity int representing the maximum number of "outgoing" connections from the point

# Graph problems
There are a number of graph problems that have algorithms which can be used to solve them. Below are some of the typical problems and their defenitions.

P-median - given a set of nodes and edges that create assignments between them. The challenge is to find the cheapest combination. This typically gives the most central point. This can also be done to find n number of assignments.

Prize collecting steiner tree - similar to the minimum spanning tree problem where all nodes need to be covered the prize collecting problem gives a prize p at nodes n such that they are connected in s sub trees.

Capacitated p-median - following the defenition of the p-median an additional requirement is added. Connect at most p demand points/assignments.

Edge disjoint capacitated p-median - when solving the p-median problem it may require the use of overlapping edges. This is contrary to many requirements of engineering problems where there is no overlap allowed.

Capacitated network flow - given a set of possible locations create the minimum cost footprint with at most some max number of connections.

Graph partitioning - find the best place to divide a graph such that it can be truned into g sub-graphs.

# INSTALL
Goto [here](https://github.com/fhk/link_src/blob/master/INSTALL.md).

## HOWTO

Running the functionality as a module

```
from link.solve.main import run_pcst

input = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "geometry":
        {"type": "LineString", "coordinates":
            [[-122.038761, 36.959798], [-122.03883969999995, 36.9598438]]},
        "properties": {"length": 9.158584651879671}}
    {"type": "Feature", "geometry":
        {"type": "Point", "coordinates":
             [-122.03883969999995, 36.9598438]},
        "properties": {
            "capacity": 1000,
            "candidate": 500}}
    {"type": "Feature", "geometry":
        {"type": "Point", "coordinates":
            [-122.03883969999995, 36.9598438]},
        "properties": {
            "capacity": 0,
            "candidate": 0,
            "demand": 1}}
]}

result = run_pcst(input)
```

Running the functionality as an API

### Python

```
import requests

input = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "geometry":
        {"type": "LineString", "coordinates":
            [[-122.038761, 36.959798], [-122.03883969999995, 36.9598438]]},
        "properties": {"length": 9.158584651879671}}
    {"type": "Feature", "geometry":
        {"type": "Point", "coordinates":
             [-122.03883969999995, 36.9598438]},
        "properties": {
            "capacity": 1000,
            "candidate": 500}}
    {"type": "Feature", "geometry":
        {"type": "Point", "coordinates":
            [-122.03883969999995, 36.9598438]},
        "properties": {
            "capacity": 0,
            "candidate": 0,
            "demand": 1}}
]}

url = "0.0.0.0/v1/pcst/submit"
result = request.post(url, json=input)
```

### JS

```
var input = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "geometry":
        {"type": "LineString", "coordinates":
            [[-122.038761, 36.959798], [-122.03883969999995, 36.9598438]]},
        "properties": {"length": 9.158584651879671}}
    {"type": "Feature", "geometry":
        {"type": "Point", "coordinates":
             [-122.03883969999995, 36.9598438]},
        "properties": {
            "capacity": 1000,
            "candidate": 500}}
    {"type": "Feature", "geometry":
        {"type": "Point", "coordinates":
            [-122.03883969999995, 36.9598438]},
        "properties": {
            "capacity": 0,
            "candidate": 0,
            "demand": 1}}
]};

var res = $.ajax({
    'url': '/v1/pcst/submit',
    'type': 'POST',
    'data': JSON.stringify(input),
    'contentType': 'application/json',
    'async': False
});

```

### TODO
There is an example jupyter notebook which shows you an end to end example [here](https://github.com/fhk/link_src/blob/master/notebooks/demo.ipynb). 

You can also run the whole suite with some test data to benchmark the existing functionality or something tha you add [here](https://github.com/fhk/test_data).

## Examples, Slides, DEMOS
Goto [here](https://github.com/fhk/link_demo).

## Endpoints

The REST API works as follows.

1. Submit GeoJSON Feature Collection
2. Hit a endpoint
    {your_url}/{version}/{method}/submit
    Current version is "v1"
    Methods include "pcst", "pmed", "nfmp", "spamp", "pamp"
    e.g.
    "your_url/v1/pcst/submit"
3. The solution should be returned

# Reference this and the link framework research

DOI 10.17605/OSF.IO/3PZJ8

# GPL functionality

The GPL modules used in this project are considered optional as functionality exists such that they provide user installable improvements.

Please be advised that you are responsible for complying with GPL requirements and deciding if they are aligned with your project/usage.

Therefore, It is optional to install the following libraries:

1. [graph-tool](https://graph-tool.skewed.de/) - this yields a siginificant improvement in the speed at which you can interact with large graphs.
2. [t-bart](https://cran.r-project.org/web/packages/tbart/index.html) R module - this is an implementation of Tietz-Bart in R which is an alternative to the pmed implementation of a assignment/p-median modelling approach.

# Shout out

Thanks to fraenkel-lab and their [pcst_fast](https://github.com/fraenkel-lab/pcst_fast) module.

# License

!!!Pending!!! Still working out the GPL challenges as this functionality is new and also includes commerical closed source functionality.

This software is shared under MIT see license file [here](https://github.com/fhk/link_src/blob/master/LICENSE.md).

### Flask wrapping concept taken from: [Flask boilerplate code](https://github.com/MaxHalford/flask-boilerplate)

# Contributing

This project is very new and it is expected that there are bugs and short comings in the way to functionality can be used.

Please add tickets using the Github tracker [here](https://github.com/fhk/link_src/issues)

You can join and/or see the overall project [here](https://github.com/users/fhk/projects/1) 

## Bugs

Please report any bugs that you find and that are reproducible. Either by creating a unit test pull request or uploading test data as part of the ticket.

## Features/Enhancements

Overall the scope of the project focusses on the use of graphs for find solutions to geospatial problems. This includes concepts like:

- deriving topology from one graph into another.
- finding routes using Travelling Salesman Problem (TSP) methods.
- adding solvers or search methods.
- reproducting and/or sharing research.
- implementing text book formulations or methods in alternative technologies for comparison.
- ...

If there is anything that you think might be of interst please sub a ticket.
