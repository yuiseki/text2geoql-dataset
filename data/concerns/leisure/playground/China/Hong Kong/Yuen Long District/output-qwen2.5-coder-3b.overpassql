[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["leisure"~"playground"](area.outer);
);
out geom;
