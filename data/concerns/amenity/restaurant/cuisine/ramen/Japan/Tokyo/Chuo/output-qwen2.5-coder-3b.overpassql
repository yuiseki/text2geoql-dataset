[out:json][timeout:30];
area["name:ja"="東京都"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"ramen"](area.outer);
);
out geom;
