[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gwanak-gu"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
