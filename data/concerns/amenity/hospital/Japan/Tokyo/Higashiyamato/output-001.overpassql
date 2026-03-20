[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Higashiyamato"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
