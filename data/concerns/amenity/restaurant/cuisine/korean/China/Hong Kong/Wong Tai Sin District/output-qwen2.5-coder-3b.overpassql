[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["amenity"~"restaurant"]["cuisine"~"korean"](area.outer);
);
out geom;
