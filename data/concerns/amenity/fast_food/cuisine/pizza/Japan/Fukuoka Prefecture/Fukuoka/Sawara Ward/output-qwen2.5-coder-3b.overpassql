[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Sawara Ward"]->.inner;
(
  nwr["amenity"="fast_food"]["cuisine"="pizza"](area.inner)(area.outer);
);
out geom;
