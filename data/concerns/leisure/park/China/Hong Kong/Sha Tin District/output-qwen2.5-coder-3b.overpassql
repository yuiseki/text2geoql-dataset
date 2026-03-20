[out:json][timeout:30];
area["name:en"="Sha Tin District"]->.outer;
(
  nwr["leisure"~"park"](area.outer);
);
out geom;
