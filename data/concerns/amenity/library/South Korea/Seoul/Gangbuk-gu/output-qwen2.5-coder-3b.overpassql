[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangbuk-gu"]->.inner;
(
  nwr["amenity"="library"](area.inner)(area.outer);
);
out geom;
