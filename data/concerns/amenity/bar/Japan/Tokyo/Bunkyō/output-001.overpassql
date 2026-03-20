[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Bunkyō"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
