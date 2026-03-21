[out:json][timeout:30];
area["name:en"="Islands District"]->.outer;
(
  nwr["leisure"~"playground"](area.outer);
);
out geom;
