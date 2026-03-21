[out:json][timeout:30];
area["name:en"="Yau Tsim Mong District"]->.outer;
(
  nwr["leisure"~"playground"](area.outer);
);
out geom;
