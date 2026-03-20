// Important note: Sushi shops are typically found in sushi restaurants or specialized establishments.
[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Arakawa"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"~"sushi"](area.inner)(area.outer);
);
out geom;
