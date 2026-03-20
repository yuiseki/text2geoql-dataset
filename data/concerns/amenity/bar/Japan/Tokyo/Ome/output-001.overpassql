[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Ome"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
