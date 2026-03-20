[out:json][timeout:30];
area["name:ja"="小豆島"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"ramen"](area.outer);
);
out geom;
