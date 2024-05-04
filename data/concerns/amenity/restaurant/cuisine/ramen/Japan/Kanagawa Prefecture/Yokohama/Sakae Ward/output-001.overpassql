[out:json][timeout:30000];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Sakae Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
