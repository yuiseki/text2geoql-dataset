[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Saitama Prefecture"]->.inner;
(
  nwr["cuisine"~"mexican"](area.inner)(area.outer);
);
out geom;
