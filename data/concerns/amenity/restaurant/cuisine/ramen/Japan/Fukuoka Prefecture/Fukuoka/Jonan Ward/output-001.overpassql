[out:json][timeout:30000];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Jonan Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
