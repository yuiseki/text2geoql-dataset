[out:json][timeout:30];
area["name:en"="Sha Tin District"]->.outer;
(
  nwr["building"~"shrine"](area.outer);
);
out geom;
