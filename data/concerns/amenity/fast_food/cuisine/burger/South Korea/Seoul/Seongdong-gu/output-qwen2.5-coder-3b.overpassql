[out:json][timeout:30];
area["name:en"="Seongdong-gu"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"burger"](area.outer);
);
out geom;
