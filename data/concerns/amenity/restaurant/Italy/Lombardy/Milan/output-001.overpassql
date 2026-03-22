[out:json][timeout:30];
area["name:en"="Lombardy"]->.outer;
area["name:en"="Milan"]->.inner;
(
  nwr["amenity"="restaurant"](area.inner)(area.outer);
);
out geom;