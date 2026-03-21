[out:json][timeout:30];
area["name:en"="Kwun Tong District"]->.outer;
(
  nwr["leisure"~"playground"](area.outer);
);
out geom;
