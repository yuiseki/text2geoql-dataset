[out:json][timeout:30];
area["name:ko"="강북구"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"pizza"](area.outer);
);
out geom;
