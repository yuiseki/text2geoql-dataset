[out:json][timeout:30];
area["name:en"="Sapporo"]->.outer;
area["name:en"="Nishi Ward"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;