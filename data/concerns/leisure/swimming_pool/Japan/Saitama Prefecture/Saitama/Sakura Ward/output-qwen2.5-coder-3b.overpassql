[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Saitama Prefecture"]->.inner;
(
  nwr["leisure"="swimming_pool"](area.inner)(area.outer);
);
out geom;
