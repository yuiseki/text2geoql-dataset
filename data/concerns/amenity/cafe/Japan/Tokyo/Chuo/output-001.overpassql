[out:json][timeout:30000];
area["name:en"="Chuo"]->.outer;
area["name:en"="Tokyo"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
