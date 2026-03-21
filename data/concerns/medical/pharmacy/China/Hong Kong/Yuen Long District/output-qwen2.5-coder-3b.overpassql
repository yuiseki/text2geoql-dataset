[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["amenity"~"pharmacy"](area.outer);
);
out geom;
