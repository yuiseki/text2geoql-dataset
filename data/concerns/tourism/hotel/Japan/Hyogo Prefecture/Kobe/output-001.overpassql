// Important note: Hotal is not an amenity. "amenity"="hotel" is wrong!
[out:json][timeout:30];
area["name:en"="Hyogo Prefecture"]->.outer;
area["name:en"="Kobe"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
