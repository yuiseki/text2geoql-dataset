[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Setagaya"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
