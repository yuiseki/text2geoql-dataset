[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Nakano"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
