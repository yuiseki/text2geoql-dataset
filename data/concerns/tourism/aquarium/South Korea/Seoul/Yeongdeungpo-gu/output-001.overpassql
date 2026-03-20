[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Yeongdeungpo-gu"]->.inner;
(
  nwr["tourism"="aquarium"](area.inner)(area.outer);
);
out geom;
