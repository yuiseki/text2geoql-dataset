[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["amenity"~"hospital"](area.outer);
);
out geom;
