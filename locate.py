# Imports
import gmplot
from gmplot.writer import _Writer
from telethon.sync import TelegramClient, functions, types
from telethon.errors import SessionPasswordNeededError
import argparse
import getpass
from random import randrange
import json
from time import sleep
import math

# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--number", "-n", dest="NUMBER",
                    help="Telephone number", required=True)
parser.add_argument("--latitude", "-la", dest="LATITUDE", type=float,
                    help="Latitude of your starting location", required=True)
parser.add_argument("--longitude", "-lo", dest="LONGITUDE", type=float,
                    help="Longitude of your starting location", required=True)
parser.add_argument("--offset", "-o", dest="OFFSET", type=float,
                    help="Trilateration scanning offset", default=0.0007)

args = parser.parse_args()

# Authentication
api_id = 760605
api_hash = "5ea1a2f93b1d038e328c012846a35b13"
number = args.NUMBER

client = TelegramClient("location", api_id, api_hash)
client.connect()

if not client.is_user_authorized():
    client.send_code_request(number)
    code = input("Code: ")
    password = getpass.getpass("Password: ")
    try:
        client.sign_in(number, code)
    except SessionPasswordNeededError:
        client.sign_in(password=getpass.getpass())


def locate(lat, long):
    request = functions.contacts.GetLocatedRequest(
        geo_point=types.InputGeoPoint(lat, long),
        self_expires=1
    )

    result = client(request)

    users = []
    for user in result.users:
        name = str(user.first_name)
        if user.last_name is not None:
            name += " " + str(user.last_name)

        distance = -1
        for peer in result.updates[0].peers:
            if not isinstance(peer, types.PeerLocated):
                continue
            if peer.peer.user_id == user.id:
                distance = peer.distance
                break

        if (distance != -1):
            users.append({
                "name": name,
                "distance": distance,
                "id": user.id
            })

    return users


# Locating
cords = []
centers = []

la = args.LATITUDE
lo = args.LONGITUDE
offset = args.OFFSET

R = 6378.137
dLat = (la) * math.pi / 180 - (la + offset) * math.pi / 180
a = math.sin(dLat/2) ** 2
c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
dx = R * c * 1000

dLon = (lo) * math.pi / 180 - (lo + offset) * math.pi / 180
a = math.cos(la * math.pi / 180) ** 2 * math.sin(dLon/2) ** 2
c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
dy = R * c * 1000

print("Scanning at the starting point...", flush=True)
centers.append((la, lo))
users = locate(la, lo)
cords.append(users)
sleep(dx / 10)

print("Scanning at the offset point...", flush=True)
centers.append((la + offset, lo))
users = locate(la + offset, lo)
cords.append(users)
sleep((dy ** 2 + dx ** 2) ** (1/2) / 10)

print("Scanning at the callibration point...", flush=True)
centers.append((la, lo + offset))
users = locate(la, lo + offset)
cords.append(users)

'''
# OLD CODE FOR MANUAL TRILATERATION
for i, user in enumerate(cords[0]):
    print(str(i) + ") " + user["name"])

while True:
    id = int(input("ID: "))
    print("Locating " + cords[0][id]["name"] +
          " (#" + str(cords[0][id]["id"]) + ")")
    id = cords[0][id]["id"]

    gmap = gmplot.GoogleMapPlotter(la, lo, 16)

    for i, users in enumerate(cords):
        for user in users:
            if (user["id"] == id):
                print("Distance: " + str(user["distance"]) + "m")
                gmap.circle(
                    centers[i][0],
                    centers[i][1],
                    user["distance"],
                    face_alpha=0,
                    edge_color="#ff0000"
                )
                break
'''

print("Generating map...")
gmap = gmplot.GoogleMapPlotter(la, lo, 16)

for user in cords[0]:
    distances = []
    # Put all user's distances together
    for users in cords:
        for x in users:
            if (user["id"] == x["id"]):
                distances.append(x["distance"])
    if (len(distances) < 3):
        print("Unable to locate " + user["name"])
        continue

    x = (distances[0] ** 2 - distances[1] ** 2 + dx ** 2) \
        / (2 * dx)
    y = (distances[0] ** 2 - x ** 2) ** (1/2)

    # Reverse dx
    c = x / (R * 1000)
    a = math.tan(c / 2) ** 2 / (1 + math.tan(c / 2) ** 2)
    dLat = math.asin(a ** (1/2)) * 2
    offsetX = ((la) * math.pi / 180 - dLat) * 180 / math.pi - la
    offsetX = math.copysign(offsetX, x)

    # Reverse dy
    c = y / (R * 1000)
    a = math.tan(c / 2) ** 2 / (1 + math.tan(c / 2) ** 2)
    dLon = math.asin((a / math.cos(la * math.pi / 180) ** 2) ** (1/2)) * 2
    offsetY = ((lo) * math.pi / 180 - dLon) * 180 / math.pi - lo

    distPos = abs((x ** 2 + (dy + y) ** 2) ** (1/2) - distances[2])
    distNeg = abs((x ** 2 + (dy - y) ** 2) ** (1/2) - distances[2])
    if (distNeg < distPos):
        offsetY = -offsetY

    gmap.marker(
        la + offsetX,
        lo + offsetY,
        label=user["name"][0],
        info_window=user["name"].replace("\"", "") +
        " [±" + f"{min(distPos, distNeg):9.2f}" + "m]",
        title=user["name"].replace("\"", ""),
        color="cyan"
    )

print("Done!")
# Google's free API key
gmap.apikey = "AIzaSyDeRNMnZ__VnQDiATiuz4kPjF_c9r1kWe8"
with open("map.html", 'w', encoding="utf-8") as f:
    with _Writer(f) as w:
        gmap._write_html(w)
