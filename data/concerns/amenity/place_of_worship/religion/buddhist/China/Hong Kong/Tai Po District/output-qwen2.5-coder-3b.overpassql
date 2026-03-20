[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["building"~"temple"](area.outer);
);
out geom;
