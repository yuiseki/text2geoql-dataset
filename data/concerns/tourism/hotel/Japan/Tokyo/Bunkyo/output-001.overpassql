// Important note: Hotal is not an amenity. "amenity"="hotel" is wrong!
[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Bunkyō"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
