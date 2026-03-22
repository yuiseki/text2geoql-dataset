[out:json][timeout:30];
area["name:en"="Hokkaido"]->.outer;
area["name:en"="Sapporo"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;