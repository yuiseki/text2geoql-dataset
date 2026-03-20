[out:json][timeout:30];
area["name:en"="Asahi Ward"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"ramen"](area.outer);
);
out geom;
