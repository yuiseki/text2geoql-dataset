[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Taito"]->.inner;
(
  nwr["building"="mosque"](area.inner)(area.outer);
);
out geom;
