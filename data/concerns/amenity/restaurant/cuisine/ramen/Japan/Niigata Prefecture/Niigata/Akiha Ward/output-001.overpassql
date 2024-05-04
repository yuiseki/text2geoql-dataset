[out:json][timeout:30000];
area["name:en"="Niigata"]->.outer;
area["name:en"="Akiha Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
