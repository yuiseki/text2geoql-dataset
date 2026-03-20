[out:json][timeout:30];
area["name:ko"="강동구"]->.outer;
(
  nwr["amenity"="fast_food"]["cuisine"~"pizza"](area.outer);
);
out geom;
