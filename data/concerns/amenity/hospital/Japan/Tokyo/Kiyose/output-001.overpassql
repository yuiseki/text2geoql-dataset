[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Kiyose"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
