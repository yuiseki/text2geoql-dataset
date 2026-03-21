[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["amenity"~"restaurant"]["cuisine"~"korean"](area.outer);
);
out geom;
