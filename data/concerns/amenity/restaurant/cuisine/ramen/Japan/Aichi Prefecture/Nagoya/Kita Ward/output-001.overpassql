[out:json][timeout:30];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Kita Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
