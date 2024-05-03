[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Bunkyō"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
