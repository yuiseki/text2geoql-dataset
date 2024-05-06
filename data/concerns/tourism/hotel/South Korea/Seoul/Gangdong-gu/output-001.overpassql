[out:json][timeout:30000];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangnam-gu"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
