[out:json][timeout:30];
area["name:ko"="강서구"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"pizza"](area.outer);
);
out geom;
