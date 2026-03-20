[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Kita"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
