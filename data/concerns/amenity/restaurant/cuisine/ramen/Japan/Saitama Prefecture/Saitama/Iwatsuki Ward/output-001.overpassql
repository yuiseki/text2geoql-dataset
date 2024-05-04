[out:json][timeout:30000];
area["name:en"="Saitama"]->.outer;
area["name:en"="Iwatsuki Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
