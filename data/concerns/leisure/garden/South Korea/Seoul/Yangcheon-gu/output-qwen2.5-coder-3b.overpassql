[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Yangcheon-gu"]->.inner;
(
  nwr["leisure"="garden"](area.inner)(area.outer);
);
out geom;
