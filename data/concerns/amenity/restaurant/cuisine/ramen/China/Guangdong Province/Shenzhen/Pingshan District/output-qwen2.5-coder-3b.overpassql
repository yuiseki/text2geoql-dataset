[out:json][timeout:30];
area["name:zh"="龙岗区"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"ramen"](area.outer);
);
out geom;
