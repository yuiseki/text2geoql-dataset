[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["leisure"~"playground"](area.outer);
);
out geom;
