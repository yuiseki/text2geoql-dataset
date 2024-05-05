[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Shinjuku"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
