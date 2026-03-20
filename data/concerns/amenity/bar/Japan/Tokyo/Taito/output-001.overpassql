// Important note: Izakaya is just a bar. there is no special tag for Izakaya.
[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Taito"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
