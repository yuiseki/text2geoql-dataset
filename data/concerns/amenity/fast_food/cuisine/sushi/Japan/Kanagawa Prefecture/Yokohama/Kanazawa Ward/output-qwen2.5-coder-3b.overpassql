[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Kanagawa Prefecture"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="sushi"](area.inner)(area.outer);
);
out geom;
