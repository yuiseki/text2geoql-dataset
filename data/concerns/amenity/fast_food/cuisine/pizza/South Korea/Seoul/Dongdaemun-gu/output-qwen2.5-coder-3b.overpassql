[out:json][timeout:30];
area["name:ko"="동대문구"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"pizza"](area.outer);
);
out geom;
