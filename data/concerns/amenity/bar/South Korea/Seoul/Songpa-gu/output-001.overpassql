[out:json][timeout:30000];
area["name:en"="Seoul"]->.outer;
area["name:en"="Songpa-gu"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
