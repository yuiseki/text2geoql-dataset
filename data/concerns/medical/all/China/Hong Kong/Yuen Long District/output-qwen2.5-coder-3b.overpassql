[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["amenity"~"hospital|clinic"](area.outer);
);
out geom;
