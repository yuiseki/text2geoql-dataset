[out:json][timeout:30];
area["name:en"="Sai Kung District"]->.outer;
(
  nwr["leisure"~"playground"](area.outer);
);
out geom;
