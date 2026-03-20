// Important note: Sushi shops are traditional Japanese restaurants.
[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Katsushika"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="sushi"](area.inner)(area.outer);
);
out geom;
