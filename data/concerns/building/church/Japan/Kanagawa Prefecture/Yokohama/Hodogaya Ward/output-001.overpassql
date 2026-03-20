[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Hodogaya Ward"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
