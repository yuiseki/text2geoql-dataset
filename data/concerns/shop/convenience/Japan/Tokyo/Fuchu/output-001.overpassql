[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Fuchu"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
