[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["amenity"~"clinic|doctor"](area.outer);
);
out geom;
