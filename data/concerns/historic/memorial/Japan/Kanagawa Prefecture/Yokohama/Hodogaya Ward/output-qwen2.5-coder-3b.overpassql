[out:json][timeout:30];
area["name:en"="Hodogaya Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["memorial"](area.inner)(area.outer);
);
out geom;
