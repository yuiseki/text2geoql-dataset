[out:json][timeout:30];
area["name:en"="Yau Tsim Mong District"]->.outer;
(
  nwr["amenity"~"restaurant"]["cuisine"~"korean"](area.outer);
);
out geom;
