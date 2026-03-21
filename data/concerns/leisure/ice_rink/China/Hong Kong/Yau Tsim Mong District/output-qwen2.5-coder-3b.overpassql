[out:json][timeout:30];
area["name:en"="Yau Tsim Mong District"]->.outer;
(
  nwr["leisure"~"ice_rink"](area.outer);
);
out geom;
