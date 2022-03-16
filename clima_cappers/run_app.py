import sys

from analysis import climate_parameters_api
#from dash_app import app


def run():
    print("Args is:", sys.argv)
    if len(sys.argv) <= 1:
        from dash_app import app
        app.run()
    else:
        if sys.argv[1] == 'api_script':
            climate_parameters_api.run()
        else:
            print("Incorrect argument supplied. Did you mean api_script?")
