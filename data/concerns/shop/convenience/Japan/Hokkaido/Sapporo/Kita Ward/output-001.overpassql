[out:json][timeout:30];
area["name:en"="Sapporo"]->.outer;
area["name:en"="Kita Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;