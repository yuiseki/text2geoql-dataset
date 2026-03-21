[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["amenity"~"restaurant"]["cuisine"~"korean"](area.outer);
);
out geom;
