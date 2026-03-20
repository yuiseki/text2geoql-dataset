[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Nishi Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
