[out:json][timeout:30];
area["name:en"="Kohoku Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["leisure"~"ice_rink"](area.inner)(area.outer);
);
out geom;
