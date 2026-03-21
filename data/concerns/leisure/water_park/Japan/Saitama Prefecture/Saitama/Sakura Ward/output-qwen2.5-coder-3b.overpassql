[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Saitama Prefecture"]->.inner;
(
  nwr["leisure"~"water_park"](area.inner)(area.outer);
);
out geom;
