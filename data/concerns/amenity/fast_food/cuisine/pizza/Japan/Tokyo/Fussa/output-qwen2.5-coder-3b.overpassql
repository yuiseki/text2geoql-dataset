// Important note: Pizza shops are fast food, not restaurants!
[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Fussa"]->.inner;
(
  nwr["amenity"="fast_food"]["cuisine"="pizza"](area.inner)(area.outer);
);
out geom;
