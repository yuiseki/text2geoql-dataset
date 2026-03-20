[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"burger"](area.outer);
);
out geom;
