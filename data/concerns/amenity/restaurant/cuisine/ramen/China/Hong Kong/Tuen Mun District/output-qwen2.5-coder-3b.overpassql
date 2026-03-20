[out:json][timeout:30];
area["name:zh"="屯門區"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"ramen"](area.outer);
);
out geom;
