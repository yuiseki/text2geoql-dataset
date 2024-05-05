[out:json][timeout:30000];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Tsuzuki Ward"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
