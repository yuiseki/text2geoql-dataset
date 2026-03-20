[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Nakagyo Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
