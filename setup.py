from distutils.core import setup

setup(
    name='link',
    version='0.0.1',
    description='Connect all the things',
    author='Fabion Kauker',
    author_email='fkauker@3-gis.com',
    packages=["link"],
    install_requires=[
    "bcrypt==3.1.4",
    "blinker==1.4",
    "cffi==1.11.5",
    "cplex==12.8.0.0",
    "docloud==1.0.369",
    "docplex==2.9.141",
    "decorator==4.3.0",
    "Fiona==1.8.6",
    "Flask==0.10.1",
    "Flask-Admin==1.3.0",
    "Flask-Bcrypt==0.7.1",
    "Flask-DebugToolbar==0.10.0",
    "Flask-Login==0.3.2",
    "Flask-Mail==0.9.1",
    "Flask-Script==2.0.5",
    "Flask-SQLAlchemy==2.1",
    "Flask-WTF==0.12",
    "GDAL==2.2.4",
    "geopandas==0.4.0",
    "gunicorn==19.4.5",
    "itsdangerous==0.24",
    "Jinja2==2.10",
    "MarkupSafe==1.0",
    "networkx==2.1",
    "numpy==1.16.1",
    "osmnx==0.8.1",
    "pandas==0.23.4",
    "pcst-fast==1.0.7",
    "protobuf==3.15.0",
    "py3-ortools==5.1.4041",
    "pybind11==2.2.3",
    "pycparser==2.18",
    "pytest==3.7.0",
    "pytz==2016.10",
    "requests==2.19.1",
    "rpy2==2.8.6",
    "Rtree==0.8.3",
    "scipy==1.1.0",
    "Shapely==1.6.4.post1",
    "six==1.11.0",
    "SQLAlchemy==1.2.10",
    "structlog==16.1.0",
    "termcolor==1.1.0",
    "Werkzeug==0.15.3",
    "WTForms==2.1"
    ]
)
