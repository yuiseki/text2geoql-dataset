[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Koganei"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
