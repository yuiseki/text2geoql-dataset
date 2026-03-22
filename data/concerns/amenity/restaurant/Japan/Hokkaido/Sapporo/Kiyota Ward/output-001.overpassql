[out:json][timeout:30];
area["name:en"="Sapporo"]->.outer;
area["name:en"="Kiyota Ward"]->.inner;
(
  nwr["amenity"="restaurant"](area.inner)(area.outer);
);
out geom;