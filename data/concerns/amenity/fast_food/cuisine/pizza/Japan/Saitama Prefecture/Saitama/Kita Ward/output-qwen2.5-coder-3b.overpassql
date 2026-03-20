[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Kita Ward"]->.inner;
(
  nwr["amenity"="fast_food"]["cuisine"="pizza"](area.inner)(area.outer);
);
out geom;
