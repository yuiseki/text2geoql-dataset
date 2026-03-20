[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Minuma Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
