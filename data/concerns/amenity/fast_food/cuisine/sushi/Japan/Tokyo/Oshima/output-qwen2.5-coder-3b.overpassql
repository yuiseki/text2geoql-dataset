[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Oshima"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="sushi"](area.inner)(area.outer);
);
out geom;
