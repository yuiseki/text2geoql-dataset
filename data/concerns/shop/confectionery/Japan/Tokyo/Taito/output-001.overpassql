[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Taito"]->.inner;
(
  nwr["shop"="confectionery"](area.inner)(area.outer);
);
out geom;
