[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Mizuho"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
