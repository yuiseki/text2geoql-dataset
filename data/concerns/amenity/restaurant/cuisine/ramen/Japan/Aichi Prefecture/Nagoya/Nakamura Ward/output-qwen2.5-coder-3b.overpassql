[out:json][timeout:30];
area["name:en"="Nakamura Ward"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"ramen"](area.outer);
);
out geom;
