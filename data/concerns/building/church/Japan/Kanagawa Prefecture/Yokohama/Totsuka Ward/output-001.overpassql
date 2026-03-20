[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Totsuka Ward"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
