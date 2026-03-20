[out:json][timeout:30];
area["name:ko"="노원구"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"pizza"](area.outer);
);
out geom;
