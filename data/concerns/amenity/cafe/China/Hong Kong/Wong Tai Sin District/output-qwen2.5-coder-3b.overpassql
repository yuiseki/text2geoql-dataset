[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["amenity"~"cafe"](area.outer);
);
out geom;
