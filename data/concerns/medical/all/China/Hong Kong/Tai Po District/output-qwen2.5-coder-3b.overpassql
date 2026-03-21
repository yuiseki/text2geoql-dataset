[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["amenity"~"hospital|clinic"](area.outer);
);
out geom;
