[out:json][timeout:30];
area["name:en"="Yangcheon-gu"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"burger"](area.outer);
);
out geom;
