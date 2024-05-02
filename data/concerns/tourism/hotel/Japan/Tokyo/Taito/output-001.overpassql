[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Taito"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
