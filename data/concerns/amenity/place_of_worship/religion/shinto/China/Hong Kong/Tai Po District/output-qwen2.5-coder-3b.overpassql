[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["building"~"shrine"](area.outer);
);
out geom;
