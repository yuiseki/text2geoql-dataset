[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Jongno-gu"]->.inner;
(
  nwr["leisure"="playground"](area.inner)(area.outer);
);
out geom;
