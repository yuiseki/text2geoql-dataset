[out:json][timeout:30];
area["name:ja"="千住"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"ramen"](area.outer);
);
out geom;
