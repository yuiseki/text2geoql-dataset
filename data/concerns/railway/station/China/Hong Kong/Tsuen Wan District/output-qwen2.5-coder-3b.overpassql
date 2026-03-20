[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["railway"~"station"](area.outer);
);
out geom;
