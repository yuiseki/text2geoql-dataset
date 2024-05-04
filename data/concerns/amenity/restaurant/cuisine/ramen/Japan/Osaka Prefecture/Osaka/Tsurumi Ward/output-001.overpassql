[out:json][timeout:30000];
area["name:en"="Osaka"]->.outer;
area["name:en"="Tsurumi Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
