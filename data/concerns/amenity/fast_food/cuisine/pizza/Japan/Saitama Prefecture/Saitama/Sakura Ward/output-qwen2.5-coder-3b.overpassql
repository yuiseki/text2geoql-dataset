[out:json][timeout:30];
area["name:ja"="桜区"]->.outer;
area["name:ja"="さいたま市"]->.inner;
(
  nwr["amenity"="fast_food"]["cuisine"="pizza"](area.inner)(area.outer);
);
out geom;
