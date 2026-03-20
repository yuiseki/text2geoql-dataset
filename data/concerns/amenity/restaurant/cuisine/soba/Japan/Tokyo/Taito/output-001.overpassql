[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Taito"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="soba"](area.inner)(area.outer);
);
out geom;
