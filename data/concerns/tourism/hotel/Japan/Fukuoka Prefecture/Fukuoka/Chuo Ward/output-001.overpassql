// Important note: Hotal is not an amenity. "amenity"="hotel" is wrong!
[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Chuo Ward"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
