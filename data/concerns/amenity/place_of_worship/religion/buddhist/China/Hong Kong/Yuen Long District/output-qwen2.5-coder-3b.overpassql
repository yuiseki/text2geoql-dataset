[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["building"~"temple"](area.outer);
);
out geom;
