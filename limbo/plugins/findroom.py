import simplejson
import requests
import re
import datetime
import pytz


def findroom_response(text):
    """!findroom (optional floor, nyc2|nyc4, default nyc2) (duration, optional, default 30) (optional meeting start time, default at the next half hour) (optional meeting date, default today): finds available conference rooms in eastern time"""

    utc = pytz.utc
    current_dt = \
        utc.localize(datetime.datetime.now()).astimezone(pytz.timezone('US/Eastern'))
    
    match = re.match(r'!findroom ?(.{4})? ?(\d{2})? ?(\d{2}\:\d{2})? ?(\d{4}\-\d{2}\-\d{2})?', text, re.IGNORECASE)
    if not match:
        return False

    # WHAT YEAR IS IT
    hour_fraction = current_dt.minute / 60.
    if hour_fraction > 0.5: # we're past the 30 currently
        target_minutes = 60-current_dt.minute # add minutes to get to the 00 of the next hour
    else:
        target_minutes = 30-current_dt.minute # start at the next :30 otherwise

    # parse args
    floor = match.group(1) or 'nyc2'
    start_date = match.group(4) or current_dt.strftime('%Y-%m-%d')
    start_time = match.group(3) or (current_dt + datetime.timedelta(minutes=target_minutes)).strftime('%H:%M:00')
    if match.group(3) != None:
        start_time += ":00"
    
    duration = match.group(2) or 30


    valid_floors = ['nyc2', 'nyc4']
    
    if floor not in valid_floors:
        return "Invalid floor."
    
    request = {'mode':'json', 'duration':duration, 'date':start_date, 'time':start_time, 'location':floor}
    result = requests.post('http://mmisiewicz.devnxs.net:7777/get_avail', data=simplejson.dumps(request))
    try:
        result_json = result.json()
    except:
        print request, result.text
        return "Something's wrong with Michael's dev server. Such sadness. It's dark."
    
    if len(result_json['available']) == 0:
        return "NO ROOMS FOR YOU!"
    op = 'Rooms available on %s for %s minutes starting at %s %s\n' % (floor, duration, start_date, start_time)
    op +='\n'.join(result_json['available'])
    return op

if __name__ == '__main__':
    print findroom_response({'body':'!findroom'})
    # print findroom({'body':'!findroom london'})
    # print findroom({'body':'!findroom nyc4'})
    # print findroom({'body':'!findroom nyc4 30'})
    # print findroom({'body':'!findroom nyc4 60'})
    # print findroom({'body':'!findroom nyc2 30 16:00'})
    # print findroom({'body':'!findroom nyc2 30 16:00 2014-11-20'})

def on_message(msg, server):
    text = msg.get("text", "")
    return findroom_response(text)