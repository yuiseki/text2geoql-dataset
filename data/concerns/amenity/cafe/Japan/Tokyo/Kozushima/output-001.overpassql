[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Kozushima"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
