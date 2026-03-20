[out:json][timeout:30];
area["name:ko"="구로구"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"sushi"](area.outer);
);
out geom;
