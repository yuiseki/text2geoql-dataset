[out:json][timeout:30];
area["name:ko"="광진구"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"ramen"](area.outer);
);
out geom;
