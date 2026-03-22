[out:json][timeout:30];
area["name:en"="Lombardy"]->.outer;
area["name:en"="Milan"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;