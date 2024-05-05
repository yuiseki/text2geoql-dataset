[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Kita"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
