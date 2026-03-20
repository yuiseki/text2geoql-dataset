[out:json][timeout:30];
area["name:ko"="강남구"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"ramen"](area.outer);
);
out geom;
