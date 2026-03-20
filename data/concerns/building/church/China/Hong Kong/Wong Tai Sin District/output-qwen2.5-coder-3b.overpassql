[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["building"~"church"](area.outer);
);
out geom;
