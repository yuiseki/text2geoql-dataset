[out:json][timeout:30];
area["name:en"="Kwai Tsing District"]->.outer;
(
  nwr["leisure"~"playground"](area.outer);
);
out geom;
