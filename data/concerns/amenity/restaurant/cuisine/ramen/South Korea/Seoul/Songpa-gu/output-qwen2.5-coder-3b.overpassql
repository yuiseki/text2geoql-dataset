[out:json][timeout:30];
area["name:ko"="송파구"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"ramen"](area.outer);
);
out geom;
