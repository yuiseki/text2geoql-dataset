[out:json][timeout:30];
area["name:ko"="영등포구"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"pizza"](area.outer);
);
out geom;
