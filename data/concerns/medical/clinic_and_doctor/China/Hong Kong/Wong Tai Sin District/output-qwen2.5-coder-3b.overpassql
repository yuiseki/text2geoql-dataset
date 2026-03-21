[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["amenity"~"clinic|doctor"](area.outer);
);
out geom;
