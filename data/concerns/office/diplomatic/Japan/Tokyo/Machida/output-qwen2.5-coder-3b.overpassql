[out:json][timeout:30];
area["name:ja"="港区"]->.outer;
area["name:en"="Tokyo"]->.inner;
(
  nwr["building"="embassy"](area.inner)(area.outer);
);
out geom;
