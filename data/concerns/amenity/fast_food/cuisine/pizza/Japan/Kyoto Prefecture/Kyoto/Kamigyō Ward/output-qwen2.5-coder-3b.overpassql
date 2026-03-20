[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Kamigyō Ward"]->.inner;
(
  nwr["amenity"="fast_food"]["cuisine"="pizza"](area.inner)(area.outer);
);
out geom;
