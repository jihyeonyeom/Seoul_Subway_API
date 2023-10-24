from flask import Flask, render_template, request
import requests  # pip install requests
from urllib.parse import urlencode, unquote
import json
from dotenv import load_dotenv
import pymysql
import os

app = Flask(__name__)  # Initialise app

load_dotenv()
mySubwayKey = os.environ.get("SEOUL_SUBWAY_KEY")


item = []
def getSeoulSubway(subway_name, updn_Line):
    url = "http://swopenAPI.seoul.go.kr/api/subway/" + mySubwayKey + "/json/realtimePosition/0/100/" + subway_name
    response = requests.get(url)
    r_dict = json.loads(response.text)
    r_items = r_dict.get("realtimePositionList")
    updnLine_num = '0' if updn_Line == "상행" else '1'
    item.clear()
    if r_items:
        for r_item in r_items:
            if r_item["updnLine"] == updnLine_num:
                item.append(r_item)
            else:
                pass
    return item

def getSubwayArrive(station_name, updn_Line):
    url = "http://swopenAPI.seoul.go.kr/api/subway/" + mySubwayKey + "/json/realtimeStationArrival/0/100/" + station_name
    response = requests.get(url)
    r_dict = json.loads(response.text)
    r_items = r_dict.get("realtimeArrivalList")
    item.clear()
    for r_item in r_items:
        if r_item["updnLine"] == updn_Line:
            item.append(r_item)
        else:
            pass
    return item

def list_chunk(lst, n):
    items = []
    if n > len(lst):
        for i in range(len(lst) - len(lst) % 10, len(lst)):
            items.append(lst[i])
    else:
        for i in range(n - 10, n):
            items.append(lst[i])
    return items

@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/subway/view")
def subway_view():
    return render_template("subway-view.html")

@app.route("/route/realtime")
def route_realtime():
    return render_template("route-realtime.html")

@app.route("/subway/arrive")
def subway_arrive():
    return render_template("subway-arrive.html")

@app.route("/route/realtime/action", methods=["GET", "POST"])
def route_action():
    if request.method == "POST":
        subway_line = request.form["subway_line"]
        updn_Line = request.form["updn_Line"]
        page = request.args.get('page', type=int, default=1)
        
        if subway_line == None:
            return render_template("route-realtime.html")
        
        items = getSeoulSubway(subway_line, updn_Line)
        items = list_chunk(items, 10)
        item_count = len(item) / 10 if len(item) % 10 == 0 else int(len(item) / 10 + 1)
        return render_template(
            "route-realtime.html",
            page = page,
            items = items,
            item_count = item_count,
        )
    else:
        page = request.args.get('page', type=int, default=1)
        items = list_chunk(item, page * 10)
        item_count = len(item) / 10 if len(item) % 10 == 0 else int(len(item) / 10 + 1)
        return render_template(
            "route-realtime.html",
            page = page,
            items = items,
            item_count = item_count,
        )
        
@app.route("/subway/arrive/action", methods=["GET", "POST"])
def arrive_action():
    if request.method == "POST":
        station_name = request.form["station_name"]
        updn_Line = request.form["updn_Line"]
        page = request.args.get('page', type=int, default=1)
        
        if station_name == None:
            return render_template("subway-arrive.html")
        
        items = getSubwayArrive(station_name, updn_Line)
        items = list_chunk(items, 10)
        item_count = len(item) / 10 if len(item) % 10 == 0 else int(len(item) / 10 + 1)
        return render_template(
            "subway-arrive.html",
            page = page,
            items = items,
            item_count = item_count,
        )
    else:
        page = request.args.get('page', type=int, default=1)
        items = list_chunk(item, page * 10)
        item_count = len(item) / 10 if len(item) % 10 == 0 else int(len(item) / 10 + 1)
        return render_template(
            "subway-arrive.html",
            page = page,
            items = items,
            item_count = item_count,
        )

if __name__=="__main__":
    app.run(debug=True)