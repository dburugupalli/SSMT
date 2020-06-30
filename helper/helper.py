import constants
import datetime

class Helper:

    def getRequestHeader(self):
        if constants.OPENSHIFT_TOKEN == False:
            return "Please set environment variables, execute config.sh first"
        headers = {'Authorization': 'Bearer ' + constants.OPENSHIFT_TOKEN,
        'Accept': 'application/json', 'Content-Type': 'application/json'}
        return headers
    
    def getOneHour(self):
        now = datetime.datetime.utcnow()
        period_end = now.strftime("%Y-%m-%d"+"T"+"%H:00:00"+"Z")
        hour = int(now.strftime("%H"))
        if hour == 0: 
            hour = '23'
        else:
            hour = str(hour-2)
        if int(hour) < 12: 
            period_start = now.strftime("%Y-%m-%d"+"T0") + hour + ":00:00Z"
        else:
            period_start = now.strftime("%Y-%m-%d"+"T") + hour + ":00:00Z"
        return period_start, period_end