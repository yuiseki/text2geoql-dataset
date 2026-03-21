[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["leisure"~"garden"](area.outer);
);
out geom;
