[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["amenity"~"pharmacy"](area.outer);
);
out geom;
