[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Nowon-gu"]->.inner;
(
  nwr["amenity"="police"](area.inner)(area.outer);
);
out geom;
