[out:json][timeout:30000];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gwanak-gu"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
