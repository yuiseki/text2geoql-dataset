[out:json][timeout:30];
area["name:ko"="광진구"]->.outer;
(
  nwr["amenity"="fast_food"]["cuisine"~"pizza"](area.outer);
);
out geom;
