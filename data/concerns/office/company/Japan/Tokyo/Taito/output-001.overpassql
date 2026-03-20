[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Taito"]->.inner;
(
  nwr["office"="company"](area.inner)(area.outer);
);
out geom;
