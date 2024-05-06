[out:json][timeout:30000];
area["name:en"="Seoul"]->.outer;
area["name:en"="Seongdong-gu"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
