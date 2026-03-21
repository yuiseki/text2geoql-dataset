[out:json][timeout:30];
area["name:en"="Kwai Tsing District"]->.outer;
(
  nwr["amenity"~"hospital|clinic"](area.outer);
);
out geom;
