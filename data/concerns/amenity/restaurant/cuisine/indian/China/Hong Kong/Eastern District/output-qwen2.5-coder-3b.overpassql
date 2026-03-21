[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["amenity"="restaurant"]["cuisine"~"indian"](area.outer);
);
out geom;
