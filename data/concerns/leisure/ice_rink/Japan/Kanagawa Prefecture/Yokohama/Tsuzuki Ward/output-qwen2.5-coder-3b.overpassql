[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Kanagawa Prefecture"]->.inner;
(
  nwr["leisure"~"ice_rink"](area.inner)(area.outer);
);
out geom;
