[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["building"~"church"](area.outer);
);
out geom;
