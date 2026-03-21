[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Seongbuk-gu"]->.inner;
(
  nwr["amenity"="library"](area.inner)(area.outer);
);
out geom;
