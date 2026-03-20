[out:json][timeout:30];
area["name:ja"="福岡県"]->.outer;
area["name:ja"="福岡市"]->.inner;
(
  nwr["amenity"="fast_food"]["cuisine"="pizza"](area.inner)(area.outer);
);
out geom;
