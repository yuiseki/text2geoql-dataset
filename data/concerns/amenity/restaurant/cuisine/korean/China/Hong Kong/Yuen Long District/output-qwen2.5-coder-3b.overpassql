[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["amenity"~"restaurant"]["cuisine"~"korean"](area.outer);
);
out geom;
