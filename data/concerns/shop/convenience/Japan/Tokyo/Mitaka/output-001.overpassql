[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Mitaka"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
