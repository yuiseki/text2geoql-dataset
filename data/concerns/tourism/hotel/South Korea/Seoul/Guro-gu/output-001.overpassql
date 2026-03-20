[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Guro-gu"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
