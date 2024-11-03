import os
import googlemaps
import pandas as pd

api_key_dir = os.path.dirname(os.path.abspath(__file__))
file = open(os.path.join(api_key_dir, "API Key")) #Add your own API key.
key = file.readline()
file.close()
gmaps = googlemaps.Client(key = key)

steder = ["Landøya", "Torstad", "Solvang", "Borgen", "Risenga", "Vollen", "Hovedgården", "Slemmestad", "Røyken", "Spikkestad", "Sætre", "Tofte"]
geocode_result = [gmaps.geocode(i + ", Asker, Norge") for i in steder]

lats = [i[0]["geometry"]["location"]["lat"] for i in geocode_result]
lngs = [i[0]["geometry"]["location"]["lng"] for i in geocode_result]

df = pd.DataFrame({"steder": steder, "latitudes": lats, "longitudes": lngs})

df.to_csv(os.path.join(api_key_dir, "soner_gps.csv"))

stem = "https://maps.googleapis.com/maps/api/distancematrix/json?"
latlng = [f"{str(lats[i])}%2C-{str(lngs[i])}" for i in range(len(lats))]
urls = [f"{stem}destinations={'|'.join(latlng[j] for j in range(len(latlng)) if j != i)}&origins={latlng[i]}&key={key}" for i in range(len(latlng))]

for i in urls: print(i, "\n\n")