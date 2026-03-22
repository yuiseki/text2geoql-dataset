[out:json][timeout:30];
area["name:en"="Sapporo"]->.outer;
area["name:en"="Toyohira Ward"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;