[out:json][timeout:30];
area["name:ko"="종로구"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"pizza"](area.outer);
);
out geom;
