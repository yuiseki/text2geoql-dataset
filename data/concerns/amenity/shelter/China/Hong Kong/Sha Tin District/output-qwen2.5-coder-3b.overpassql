[out:json][timeout:30];
area["name:en"="Sha Tin District"]->.outer;
(
  nwr["building"~"shelter"](area.outer);
);
out geom;
