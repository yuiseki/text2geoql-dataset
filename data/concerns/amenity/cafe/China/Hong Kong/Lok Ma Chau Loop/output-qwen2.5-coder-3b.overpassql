[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["amenity"~"cafe"](area.outer);
);
out geom;
