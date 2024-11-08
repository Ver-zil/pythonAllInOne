import datetime


def timestamp2time(timestamp):
    dt_object = datetime.datetime.utcfromtimestamp(timestamp)

    # 格式化datetime对象为字符串
    dt_string = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return dt_string
