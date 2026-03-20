[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"ramen"](area.outer);
);
out geom;
