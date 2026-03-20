[out:json][timeout:30];
area["name:ko"="중랑구"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"pizza"](area.outer);
);
out geom;
