from application.Connections import Connection
from time import gmtime, strftime, time

def getDateHashtags(alertid, date):
    return list(Connection.Instance().db[str(alertid)].aggregate([
        {
            '$match': {
                'timestamp_ms': {'$gte': str(date)}
            }
        },
        {
            '$unwind': '$entities.hashtags'
        },
        {
            '$group': {
                '_id': '$entities.hashtags.text',
                'count': {
                    '$sum': 1
                }
            }
        },
        {
            '$project': {
                'count':1,
                'hashtag': '$_id',
                '_id':0
            }
        },
        {
            '$sort': {'count':-1}
        },
        {'$limit':20}
    ]))

def calculate_dates():
    l = []
    current_milli_time = int(round(time() * 1000))
    one_day = 86400000
    l.append(('yesterday', current_milli_time - one_day))
    l.append(('week', current_milli_time - 14 * one_day))
    l.append(('month', current_milli_time - 30 * one_day))
    return l

def calc(alertid):
    dates = calculate_dates()
    for date, current_milli_time in dates:
        result = {
            'name': date,
            date: getDateHashtags(alertid, current_milli_time),
            'modified_date': strftime("%a, %d %b %Y %H:%M:%S", gmtime())
        }
        if result[date] != []:
            Connection.Instance().hashtags[str(alertid)].remove({'name': result['name']})
            Connection.Instance().hashtags[str(alertid)].insert_one(result)

if __name__ == '__main__':
    Connection.Instance().cur.execute("Select alertid from alerts;")
    alert_list = Connection.Instance().cur.fetchall()
    for alert in alert_list:
        calc(alert[0])
