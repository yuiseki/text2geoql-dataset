[out:json][timeout:30000];
area["name:en"="Seoul"]->.outer;
area["name:en"="Yangcheon-gu"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
