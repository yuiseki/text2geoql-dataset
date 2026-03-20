[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Sumida"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
