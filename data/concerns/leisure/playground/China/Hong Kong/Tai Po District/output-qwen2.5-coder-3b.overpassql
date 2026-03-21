[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["leisure"~"playground"](area.outer);
);
out geom;
