import os
OPENSHIFT_TOKEN = os.environ.get("OS_OPENSHIFT_TOKEN")
FLASK_APP_URL = 'http://' + str(os.environ.get("HOST","localhost")) +':'+str(os.environ.get("PORT", 8000))
METERING_ROUTE_LIST_ALL_PROJECTS = os.environ.get("OS_LIST_ALL_PROJECTS_URL")
