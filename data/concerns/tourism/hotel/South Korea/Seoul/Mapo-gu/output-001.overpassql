[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Mapo-gu"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
