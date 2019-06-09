# INSTALL Link

Linux (Supported)
OS-X (Kinda)
Windows (Experimental)

There are a number of steps and dependencies that you can/need install including
if you intend to use the Python module, jupyter notebook or do development. Otherwise
you should just use the docker container option. Below is a list of the additional
dependencies which may take some effort to install:

- CPLEX (local)
- CPLEX (docplex - SaaS Solver)
- TBart - R module licensed under GPL
- graph-tool - graph library licensed under GPL

# The fast way

1. Create a docker image using the "Dockerfile"
    1. Note: you will need to set the CPLEX env variables, if you want to use:
        - pamp, spamp, nfmp
2. Run the docker image
3. Send data to the API using Postman
    1. Sample data can be sourced [here](https://github.com/fhk/test_data)

# Production

The implemenation is given as an example backend. Note, there is no load balancing or other bells
and whistles you would expect when deployed. In the current state you can run on your local machine
or perhaps an internal testing server.

The framework has been written for on demand container services like:

- Heroku
- Google Cloud
- AWS
- Digital ocean
- ...

The current version is ideal as acting as a very lightweight micro-service that has limited compute.

Where any MIP solving is done by the docplex api on their SaaS offering.

If you would like to learn more about the options or get access to a full service api please reach out. 

It is also possible to create new solutions for domain problems you may have.

Get in contact to scope a project/enhancement.

# The hard way

## Python environment

Yes, it's non ideal to use pip and conda but due to varying libraries across package installers
thats the way it is.

```
conda create -n link python=3.6
conda activate link
conda install fiona
pip install -r requirements.txt
```

## CPLEX (local)

You can get a trial and/or dev license [here](https://www.ibm.com/products/ilog-cplex-optimization-studio/pricing).

Then follow the install instructions [here](https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/GettingStarted/topics/set_up/setup_overview.html).

## CPLEX (remote)

Will be installed when you ran "pip install"

Now you just need to set the env varibales

```
export DO_API_KEY=your_api_key_from_ibm
export DO_URL=your_url_from_ibm
```

## R

### Linux

```
sudo apt-get install r-base
```

### OS-X

```
brew install r
```

Next run R and install the packages

```
R
install.packages("sp", "tbart")
```

## graph-tool

```
conda install graph-tool
```

or follow instructions [here](https://graph-tool.skewed.de/)

Now create the environment variables

```
export GT="1"
export TBART="1"
```

