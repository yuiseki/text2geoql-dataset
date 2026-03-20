[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["shop"~"convenience"](area.outer);
);
out geom;
