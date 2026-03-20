[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Niijima"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
