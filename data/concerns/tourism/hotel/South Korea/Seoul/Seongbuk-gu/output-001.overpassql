[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Seongbuk-gu"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
