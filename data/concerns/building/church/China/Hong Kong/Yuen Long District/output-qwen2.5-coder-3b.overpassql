[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["building"~"church"](area.outer);
);
out geom;
