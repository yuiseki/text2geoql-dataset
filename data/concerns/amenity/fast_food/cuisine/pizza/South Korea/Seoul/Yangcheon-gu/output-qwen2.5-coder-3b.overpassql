[out:json][timeout:30];
area["name:ko"="양천구"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"pizza"](area.outer);
);
out geom;
