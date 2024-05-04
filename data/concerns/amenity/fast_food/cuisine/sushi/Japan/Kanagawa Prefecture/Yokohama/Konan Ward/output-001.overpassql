[out:json][timeout:30000];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Konan Ward"]->.inner;
(
  nwr["amenity"="fast_food"]["cuisine"="sushi"](area.inner)(area.outer);
  nwr["amenity"="restaurant"]["cuisine"="sushi"](area.inner)(area.outer);
);
out geom;
