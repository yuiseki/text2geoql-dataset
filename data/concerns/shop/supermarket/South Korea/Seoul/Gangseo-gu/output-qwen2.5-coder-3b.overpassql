[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangseo-gu"]->.inner;
(
  nwr["shop"~"supermarket"](area.inner)(area.outer);
);
out geom;
