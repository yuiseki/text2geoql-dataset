[out:json][timeout:30000];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangbuk-gu"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
