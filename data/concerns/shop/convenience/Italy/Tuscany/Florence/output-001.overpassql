[out:json][timeout:30];
area["name:en"="Tuscany"]->.outer;
area["name:en"="Florence"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;