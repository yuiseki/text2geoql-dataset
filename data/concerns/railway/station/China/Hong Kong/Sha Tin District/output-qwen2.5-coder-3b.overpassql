[out:json][timeout:30];
area["name:en"="Sha Tin District"]->.outer;
(
  nwr["railway"~"station"](area.outer);
);
out geom;
