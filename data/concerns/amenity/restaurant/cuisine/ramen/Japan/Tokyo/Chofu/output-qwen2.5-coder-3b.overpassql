[out:json][timeout:30];
area["name:ja"="千代田区"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"ramen"](area.outer);
);
out geom;
