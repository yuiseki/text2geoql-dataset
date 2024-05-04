[out:json][timeout:30000];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Izumi Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
