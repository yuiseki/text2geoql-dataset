[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Urawa Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
