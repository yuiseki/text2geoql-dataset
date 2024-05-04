[out:json][timeout:30000];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Higashi Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
