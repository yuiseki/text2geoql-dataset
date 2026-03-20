[out:json][timeout:30];
area["name:en"="Wong Tai Sin District"]->.outer;
(
  nwr["building"~"temple"](area.outer);
);
out geom;
