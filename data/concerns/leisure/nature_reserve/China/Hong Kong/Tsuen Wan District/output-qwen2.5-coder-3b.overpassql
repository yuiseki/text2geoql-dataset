[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["leisure"~"nature_reserve"](area.outer);
);
out geom;
