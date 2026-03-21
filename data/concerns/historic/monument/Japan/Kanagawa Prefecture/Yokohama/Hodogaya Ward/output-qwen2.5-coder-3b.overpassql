[out:json][timeout:30];
area["name:en"="Hodogaya Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["historic"~"monument"](area.inner)(area.outer);
);
out geom;
