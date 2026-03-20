[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Ota"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
