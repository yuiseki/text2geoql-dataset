// Important note: Hotal is not an amenity. "amenity"="hotel" is wrong!
[out:json][timeout:30000];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Hakata Ward"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
