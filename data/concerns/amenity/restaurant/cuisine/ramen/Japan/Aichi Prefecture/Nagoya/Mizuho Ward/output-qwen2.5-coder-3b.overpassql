[out:json][timeout:30];
area["name:en"="Mizuho Ward"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"ramen"](area.outer);
);
out geom;
