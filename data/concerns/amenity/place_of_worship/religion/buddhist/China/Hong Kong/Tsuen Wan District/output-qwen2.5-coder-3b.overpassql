[out:json][timeout:30];
area["name:en"="Tsuen Wan District"]->.outer;
(
  nwr["building"~"temple"](area.outer);
);
out geom;
