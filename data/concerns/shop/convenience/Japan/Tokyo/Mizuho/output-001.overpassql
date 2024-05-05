[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Mizuho"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
