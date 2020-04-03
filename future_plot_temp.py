"""
A impressively small script that webscrapes data from darksky.net
given latitude and longitude. Once it does that, the script parses
the data given back many times, and finally produces a graph.
"""
import json
from datetime import datetime
import requests as requ
import numpy
from matplotlib import pyplot as plt
import tzlocal


def get_lat_long(zipcode):
    """
    Get the latitude and longitude given a zipcode.
    """
    # request the data
    data = requ.get(f'https://api.promaptools.com/service/us/zip-lat-lng/get/?zip={zipcode}&key=17o8dysaCDrgv1c')
    # make the data 'json-able':
    data = data.text.split('pre')[0]
    # json loads the data:
    data = json.loads(data)

    # for the sake of not creating more varibles, the final extraction is done here.
    return data['output'][0]['latitude'], data['output'][0]['longitude']

def get_info():
    """
    Webscrape data from darksky.net.
    """
    # Get latitude and longitude:
    lati, longi = get_lat_long(input('Enter zipcode: '))
    # request the data
    ret = requ.get(f"https://darksky.net/forecast/{lati},{longi}/us12/en")
    # make the data json-able:
    ret = ret.text.split("hours")[10]
    ret = ret.strip(" = ").split("}],")
    final_ret = ret[0]
    final_ret += "}]"
    # json loads the data
    ret = json.loads(final_ret)
    # return the final data:
    return ret

def parse():
    # Get the info.
    past_info = get_info()

    # Pre-create all lists:
    final_list = []
    unix_list = []
    humid_list = []
    cloud_list = []
    wind_list = []
    gust_list = []
    int_list = []
    pro_list = []

    # fill all lists:
    for item in past_info:
        res = item['temperature']
        final_list.append(res)
        res = item['cloudCover']
        cloud_list.append(res)
        res = item['humidity']
        humid_list.append(res*100)
        res = item['windSpeed']
        wind_list.append(res)
        res = item['time']
        unix_list.append(res)
        res = item['windGust']
        gust_list.append(res)
        res = item['precipIntensity']
        int_list.append(res)
        res = item['precipProbability']
        pro_list.append(res*100)


    # process the unix time into readable timestamps
    time_list = []

    for item in unix_list:
        unix_timestamp = float(item)
        local_timezone = tzlocal.get_localzone() # get pytz timezone
        local_time = datetime.fromtimestamp(unix_timestamp, local_timezone)
        time_list.append(local_time.strftime("%Y-%m-%d %H"))

    # create the temperature moving average:
    fin_ave = []
    hum_sum = numpy.cumsum(numpy.array(final_list))
    for index, item in enumerate(hum_sum):
        fin_ave.append(item/(index+1))


    # create the wind speed moving average:
    wind_ave = []
    hum_sum = numpy.cumsum(numpy.array(wind_list))
    for index, item in enumerate(hum_sum):
        wind_ave.append(item/(index+1))


    # create the humidty moving average:
    hum_ave = []
    hum_sum = numpy.cumsum(numpy.array(humid_list))
    for index, item in enumerate(hum_sum):
        hum_ave.append((item/(index+1)))


    # create the cloud cover moving average:
    cloud_ave = []
    hum_sum = numpy.cumsum(numpy.array(cloud_list))
    for index, item in enumerate(hum_sum):
        cloud_ave.append(item/(index+1))


    # create the wind gust moving average:
    gust_ave = []
    hum_sum = numpy.cumsum(numpy.array(gust_list))
    for index, item in enumerate(hum_sum):
        gust_ave.append(item/(index+1))


    # create the intensity of precipitation moving average:
    int_ave = []
    hum_sum = numpy.cumsum(numpy.array(int_list))
    for index, item in enumerate(hum_sum):
        int_ave.append(item/(index+1))


    # create the probability of precipitation moving average:
    pro_ave = []
    hum_sum = numpy.cumsum(numpy.array(pro_list))
    for index, item in enumerate(hum_sum):
        pro_ave.append((item/(index+1)))

    # make a dictionary of the parsed data:
    dict_of_data = {
        "pro_ave":pro_ave,
        "pro_list":pro_list,
        "int_list":int_list,
        "int_ave":int_ave,
        "hum_ave":hum_ave,
        "hum_list":humid_list,
        "fin_ave":fin_ave,
        "final_list":final_list,
        "wind_list":wind_list,
        "wind_ave":wind_ave,
        "gust_ave":gust_ave,
        "gust_list":gust_list,
        "cloud_list":cloud_list,
        "cloud_ave":cloud_ave,
        "time_list":time_list}

    # return the parsed dictionary
    return dict_of_data

def main():
    """
    Plot all of the data.
    """
    final_dict = parse()
    plt.cla()
    # create the first subplot
    plt.subplot(321)
    # x- and y- axis labels
    plt.xlabel('Time')
    plt.ylabel('Cloud Cover')
    # title
    plt.title('Cloud Cover With Moving Average')
    # plot the cloud cover data
    plt.plot(final_dict["time_list"], final_dict["cloud_list"], '-.^', color='#A9A9A9', label='Cloud Cover')
    # plot the cloud cover moving average data
    plt.plot(final_dict["time_list"], final_dict["cloud_ave"], '--s', color='#7A7A7A', label='Moving Average')
    # set the tick positions on the x-axis
    plt.xticks([0, 10, 20, 30, 40, 50])
    # create the legend
    plt.legend()

    # create the second subplot
    plt.subplot(322)
    # x- and y- axis labels
    plt.xlabel('Time')
    plt.ylabel('Temperature')
    # title
    plt.title('Temperature With Moving Average')
    # plot the temperature data
    plt.plot(final_dict["time_list"], final_dict["final_list"], '-.^', color='#00FF00', label='Temperature')
    # plot the temperature moving average data
    plt.plot(final_dict["time_list"], final_dict["fin_ave"], 'g--s', label='Moving Average')
    # set the tick positions on the x-axis
    plt.xticks([0, 10, 20, 30, 40, 50])
    # create the legend
    plt.legend()

    # create the third subplot
    plt.subplot(323)
    # x- and y- axis labels
    plt.xlabel('Time')
    plt.ylabel('% Humidity')
    # title
    plt.title('Humidity With Moving Average')
    # plot the humidty data
    plt.plot(final_dict["time_list"], final_dict["hum_list"], 'b-.^', label='Humidity')
    # plot the humidty moving average data
    plt.plot(final_dict["time_list"], final_dict["hum_ave"], 'k--s', label='Moving Average')
    # set the tick positions on the x-axis
    plt.xticks([0, 10, 20, 30, 40, 50])
    # create the legend
    plt.legend()

    # create the fourth subplot
    plt.subplot(324)
    # x- and y- axis labels
    plt.xlabel('Time')
    plt.ylabel('Miles Per Hour')
    # title
    plt.title('Wind Speed and Wind Gust With Moving Average')
    # plot the wind speed and wind gust data
    plt.plot(final_dict["time_list"], final_dict["wind_list"], '-.^', color='#00FF00', label='Wind Speed')
    plt.plot(final_dict["time_list"], final_dict["gust_list"], '--s', color='#9BFF00', label='Wind Gust Speed')
    # plot the wind speed and wind gust moving average data
    plt.plot(final_dict["time_list"], final_dict["wind_ave"], 'g--s', label='Moving Average')
    plt.plot(final_dict["time_list"], final_dict["gust_ave"], '-.^', color='#9DAF00', label='Moving Average')
    # set the tick positions on the x-axis
    plt.xticks([0, 10, 20, 30, 40, 50])
    # create the legend
    plt.legend()

    # create the fifth subplot
    plt.subplot(325)
    # x- and y- axis labels
    plt.xlabel('Time')
    plt.ylabel('Probability (%)')
    # title
    plt.title('Probability of Precipitation With Moving Average')
    # plot the probibility of precipitation data
    plt.plot(final_dict["time_list"], final_dict["pro_list"], '-.^', color='#002266', label='Probability')
    # plot the probibility of precipitation moving average data
    plt.plot(final_dict["time_list"], final_dict["pro_ave"], '--s', label='Moving Average')
    # set the tick positions on the x-axis
    plt.xticks([0, 10, 20, 30, 40, 50])
    # create the legend
    plt.legend()

    # create the sixth subplot
    plt.subplot(326)
    # x- and y- axis labels
    plt.xlabel('Time')
    plt.ylabel('Inches')
    # title
    plt.title('Intensity of Precipitation With Moving Average')
    # plot the intensity of precipitation data
    plt.plot(final_dict["time_list"], final_dict["int_list"], '-.^', color='#00FF00', label='Probability')
    # plot the intensity of precipitation moving average data
    plt.plot(final_dict["time_list"], final_dict["int_ave"], 'g--s', label='Moving Average')
    # set the tick positions on the x-axis
    plt.xticks([0, 10, 20, 30, 40, 50])
    # create the legend
    plt.legend()

    mng = plt.get_current_fig_manager()
    mng.window.showMaximized()
    plt.pause(0.001)
    plt.tight_layout()

    plt.show()

if __name__ == '__main__':
    main()
