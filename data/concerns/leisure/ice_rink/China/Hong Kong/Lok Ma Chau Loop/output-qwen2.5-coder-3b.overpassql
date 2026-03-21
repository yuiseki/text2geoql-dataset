[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["leisure"~"ice_rink"](area.outer);
);
out geom;
