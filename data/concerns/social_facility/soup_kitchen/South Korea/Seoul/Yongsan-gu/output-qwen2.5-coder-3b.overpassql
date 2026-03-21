[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Yongsan-gu"]->.inner;
(
  nwr["amenity"="food_court"](area.inner)(area.outer);
);
out geom;
