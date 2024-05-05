[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Fuchu"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
